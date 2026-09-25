# Databricks notebook source
# MAGIC %md
# MAGIC # TodayBank Session 6 - Notebook 01: Generate & Load Loan Data
# MAGIC
# MAGIC **Use case:** Consumer Loan / Credit Default Risk for TodayBank (Axos)
# MAGIC
# MAGIC This notebook generates synthetic consumer loan data in-notebook (no external files needed)
# MAGIC and writes two Unity Catalog tables:
# MAGIC - `todaybank_mlflow101.lending.loan_applications` - ~10,000 LABELED historical loans
# MAGIC - `todaybank_mlflow101.lending.new_applications` - ~200 UNLABELED fresh applications to score
# MAGIC
# MAGIC **Features (plain English):**
# MAGIC - `credit_score` - FICO-style credit score (300-850)
# MAGIC - `annual_income` - applicant annual income (USD)
# MAGIC - `dti_ratio` - debt-to-income ratio (%)
# MAGIC - `loan_amount` - requested loan amount (USD)
# MAGIC - `loan_term_months` - loan term in months (24, 36, 48, 60)
# MAGIC - `interest_rate` - annual interest rate (%)
# MAGIC - `employment_years` - years at current employer
# MAGIC - `num_prior_delinquencies` - number of past delinquencies
# MAGIC - `home_ownership` - RENT / OWN / MORTGAGE
# MAGIC - `loan_purpose` - debt_consolidation / home_improvement / auto / personal / medical

# COMMAND ----------

import numpy as np
import pandas as pd
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

# Reproducible seed - same data every run
SEED = 42
rng = np.random.default_rng(SEED)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 - Generate 10,000 labeled historical loan applications

# COMMAND ----------

N_LOANS = 10_000

# --- Correlated applicant features ---
# Credit score: normally distributed, clipped to 300-850
credit_score = rng.normal(680, 80, N_LOANS).clip(300, 850).astype(int)

# Annual income: log-normal (skewed right, like real income distributions)
annual_income = rng.lognormal(mean=10.9, sigma=0.55, size=N_LOANS).round(-2)  # ~$50k median

# DTI ratio: higher DTI = worse risk. Correlated slightly with low income.
dti_base = rng.normal(28, 10, N_LOANS)
dti_ratio = (dti_base - 0.015 * (annual_income / 1000 - 50)).clip(5, 60).round(1)

# Loan amount
loan_amount = rng.choice([5000, 10000, 15000, 20000, 25000, 35000, 50000],
                         p=[0.12, 0.22, 0.18, 0.20, 0.14, 0.09, 0.05],
                         size=N_LOANS)

# Loan term months
loan_term_months = rng.choice([24, 36, 48, 60], p=[0.10, 0.35, 0.30, 0.25], size=N_LOANS)

# Interest rate: inversely correlated with credit score
interest_rate = (26 - 0.022 * credit_score + rng.normal(0, 1.5, N_LOANS)).clip(3.5, 24.0).round(2)

# Employment years: right-skewed, more new employees
employment_years = rng.exponential(scale=4.5, size=N_LOANS).clip(0, 30).round(1)

# Number of prior delinquencies: mostly 0, occasionally more
num_prior_delinquencies = rng.choice(
    [0, 1, 2, 3, 4, 5],
    p=[0.60, 0.22, 0.10, 0.05, 0.02, 0.01],
    size=N_LOANS
)

# Categorical features
home_ownership = rng.choice(["RENT", "OWN", "MORTGAGE"], p=[0.40, 0.20, 0.40], size=N_LOANS)
loan_purpose = rng.choice(
    ["debt_consolidation", "home_improvement", "auto", "personal", "medical"],
    p=[0.40, 0.20, 0.15, 0.15, 0.10],
    size=N_LOANS
)

# --- Compute default probability (realistic risk model) ---
# Higher credit score, lower dti, more employment = lower default risk
# More delinquencies, higher loan amount, debt consolidation = higher risk
log_odds = (
    -3.5
    - 0.006  * (credit_score - 680)      # better score = less risk
    + 0.040  * (dti_ratio - 28)           # higher DTI = more risk
    - 0.010  * (employment_years - 4.5)   # more experience = less risk
    + 0.030  * num_prior_delinquencies    # prior delinquencies = more risk
    + 0.000015 * (loan_amount - 15000)    # larger loans = slightly more risk
    + (np.array(loan_purpose) == "debt_consolidation").astype(float) * 0.3  # debt consol = more risk
    + (np.array(home_ownership) == "RENT").astype(float) * 0.2              # renters = slightly more risk
)

prob_default = 1 / (1 + np.exp(-log_odds))

# Draw actual default outcome: ~7-8% base rate
defaulted = rng.binomial(1, prob_default).astype(bool)
print(f"Default rate: {defaulted.mean():.1%}  ({defaulted.sum()} of {N_LOANS})")

# --- Build DataFrame ---
df_hist = pd.DataFrame({
    "loan_id": [f"TBL{str(i).zfill(6)}" for i in range(1, N_LOANS + 1)],
    "credit_score": credit_score,
    "annual_income": annual_income.astype(int),
    "dti_ratio": dti_ratio,
    "loan_amount": loan_amount,
    "loan_term_months": loan_term_months,
    "interest_rate": interest_rate,
    "employment_years": employment_years,
    "num_prior_delinquencies": num_prior_delinquencies,
    "home_ownership": home_ownership,
    "loan_purpose": loan_purpose,
    "defaulted": defaulted,
})

print(df_hist.head(5).to_string())
print(f"\nShape: {df_hist.shape}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 - Generate 200 unlabeled new applications (to score live)

# COMMAND ----------

N_NEW = 200

# Same feature generation, no label
cs2 = rng.normal(680, 80, N_NEW).clip(300, 850).astype(int)
inc2 = rng.lognormal(10.9, 0.55, N_NEW).round(-2).astype(int)
dti2 = (rng.normal(28, 10, N_NEW) - 0.015 * (inc2 / 1000 - 50)).clip(5, 60).round(1)
la2 = rng.choice([5000, 10000, 15000, 20000, 25000, 35000, 50000],
                 p=[0.12, 0.22, 0.18, 0.20, 0.14, 0.09, 0.05], size=N_NEW)
lt2 = rng.choice([24, 36, 48, 60], p=[0.10, 0.35, 0.30, 0.25], size=N_NEW)
ir2 = (26 - 0.022 * cs2 + rng.normal(0, 1.5, N_NEW)).clip(3.5, 24.0).round(2)
ey2 = rng.exponential(4.5, N_NEW).clip(0, 30).round(1)
nd2 = rng.choice([0, 1, 2, 3, 4, 5], p=[0.60, 0.22, 0.10, 0.05, 0.02, 0.01], size=N_NEW)
ho2 = rng.choice(["RENT", "OWN", "MORTGAGE"], p=[0.40, 0.20, 0.40], size=N_NEW)
lp2 = rng.choice(["debt_consolidation", "home_improvement", "auto", "personal", "medical"],
                 p=[0.40, 0.20, 0.15, 0.15, 0.10], size=N_NEW)

df_new = pd.DataFrame({
    "application_id": [f"TBN{str(i).zfill(5)}" for i in range(1, N_NEW + 1)],
    "credit_score": cs2,
    "annual_income": inc2,
    "dti_ratio": dti2,
    "loan_amount": la2,
    "loan_term_months": lt2,
    "interest_rate": ir2,
    "employment_years": ey2,
    "num_prior_delinquencies": nd2,
    "home_ownership": ho2,
    "loan_purpose": lp2,
})

print(df_new.head(5).to_string())
print(f"\nShape: {df_new.shape}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 - Write both tables to Unity Catalog

# COMMAND ----------

CATALOG = "todaybank_mlflow101"
SCHEMA  = "lending"

spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"USE SCHEMA {SCHEMA}")

# Write labeled history
sdf_hist = spark.createDataFrame(df_hist)
(sdf_hist.write
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(f"{CATALOG}.{SCHEMA}.loan_applications"))

print(f"loan_applications written: {spark.table(f'{CATALOG}.{SCHEMA}.loan_applications').count()} rows")

# Write new (unlabeled) applications
sdf_new = spark.createDataFrame(df_new)
(sdf_new.write
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(f"{CATALOG}.{SCHEMA}.new_applications"))

print(f"new_applications written: {spark.table(f'{CATALOG}.{SCHEMA}.new_applications').count()} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 - Quick data quality check

# COMMAND ----------

print("=== loan_applications sample ===")
spark.table(f"{CATALOG}.{SCHEMA}.loan_applications").show(5)

print("\n=== Default rate breakdown ===")
spark.sql(f"""
  SELECT defaulted, COUNT(*) AS n, ROUND(COUNT(*)*100.0/SUM(COUNT(*)) OVER(), 1) AS pct
  FROM {CATALOG}.{SCHEMA}.loan_applications
  GROUP BY defaulted
  ORDER BY defaulted
""").show()

print("\n=== new_applications sample ===")
spark.table(f"{CATALOG}.{SCHEMA}.new_applications").show(3)

print("\nNotebook 01 complete. Tables ready in todaybank_mlflow101.lending")

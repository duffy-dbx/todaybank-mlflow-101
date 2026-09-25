# Databricks notebook source
# MAGIC %md
# MAGIC # TodayBank Session 6 - Notebook 04: Batch Score & Monitor Concept
# MAGIC
# MAGIC **Stages 02 WALK + 03 RUN - Register, Score, Watch**
# MAGIC
# MAGIC This notebook:
# MAGIC 1. Loads the `@champion` model directly from UC Model Registry
# MAGIC 2. Batch scores `new_applications` (200 rows) -> adds PD + risk tier
# MAGIC 3. Writes scored results to `todaybank_mlflow101.lending.loan_applications_scored`
# MAGIC 4. Prints an end-to-end lineage summary (source > model > endpoint > scored output)
# MAGIC
# MAGIC **Key concept for Axos:** Batch scoring uses the same versioned model as the
# MAGIC live endpoint. Both outputs trace back to the exact same run ID, experiment,
# MAGIC and training data - full auditability for model risk review.

# COMMAND ----------

import mlflow
import mlflow.sklearn
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, when, col
from mlflow import MlflowClient

spark = SparkSession.builder.getOrCreate()

CATALOG    = "todaybank_mlflow101"
SCHEMA     = "lending"
MODEL_UC   = f"{CATALOG}.models.loan_default_risk"
ENDPOINT   = "todaybank-loan-default"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 - Load the @champion model from UC Model Registry

# COMMAND ----------

client = MlflowClient()
champion = client.get_model_version_by_alias(name=MODEL_UC, alias="champion")
print(f"Loading @champion: {MODEL_UC}  version {champion.version}")
print(f"Run ID: {champion.run_id}")

model_uri = f"models:/{MODEL_UC}@champion"
model = mlflow.sklearn.load_model(model_uri)
print("Model loaded.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 - Load new (unlabeled) applications

# COMMAND ----------

FEATURES = [
    "credit_score", "annual_income", "dti_ratio", "loan_amount",
    "loan_term_months", "interest_rate", "employment_years",
    "num_prior_delinquencies", "home_ownership", "loan_purpose",
]

df_new = spark.table(f"{CATALOG}.{SCHEMA}.new_applications").toPandas()
print(f"New applications loaded: {len(df_new):,} rows")
df_new.head(3)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 - Score every application (batch inference)
# MAGIC
# MAGIC `model.predict()` returns the Probability of Default (PD) as a float in [0, 1].
# MAGIC We then assign a human-readable risk tier:
# MAGIC - PD < 10%  = Low risk
# MAGIC - PD 10-30% = Medium risk
# MAGIC - PD >= 30% = High risk

# COMMAND ----------

X_new = df_new[FEATURES]
pd_scores = model.predict(X_new)

df_new["pd_score"] = pd_scores
df_new["risk_tier"] = pd.cut(
    df_new["pd_score"],
    bins=[0.0, 0.10, 0.30, 1.0],
    labels=["Low", "Medium", "High"],
    right=True,
)
df_new["model_version"] = champion.version
df_new["model_run_id"]  = champion.run_id

print(f"Scored {len(df_new):,} applications")
print("\nRisk tier distribution:")
print(df_new["risk_tier"].value_counts().sort_index().to_frame())
print(f"\nMean PD: {df_new['pd_score'].mean():.4f}  |  Max PD: {df_new['pd_score'].max():.4f}")
print(df_new[["application_id", "credit_score", "dti_ratio", "pd_score", "risk_tier"]].head(10).to_string(index=False))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 - Write scored results to Unity Catalog

# COMMAND ----------

sdf_scored = spark.createDataFrame(df_new)
(sdf_scored.write
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(f"{CATALOG}.{SCHEMA}.loan_applications_scored"))

count = spark.table(f"{CATALOG}.{SCHEMA}.loan_applications_scored").count()
print(f"loan_applications_scored written: {count:,} rows")

# COMMAND ----------

# Quick sanity check
spark.sql(f"""
  SELECT risk_tier, COUNT(*) AS n, ROUND(AVG(pd_score)*100, 1) AS avg_pd_pct
  FROM {CATALOG}.{SCHEMA}.loan_applications_scored
  GROUP BY risk_tier
  ORDER BY risk_tier
""").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 - End-to-end lineage summary
# MAGIC
# MAGIC This is the governance story for Axos model risk review.
# MAGIC Every scored application traces back through an unbroken chain:

# COMMAND ----------

print("=" * 60)
print("TodayBank Session 6 - End-to-end Data & Model Lineage")
print("=" * 60)
print()
print("[1] SOURCE DATA")
print(f"    Table: {CATALOG}.{SCHEMA}.loan_applications")
print(f"    Rows:  {spark.table(f'{CATALOG}.{SCHEMA}.loan_applications').count():,} labeled historical loans")
print()
print("[2] MODEL TRAINING (MLflow)")
print(f"    Experiment:  /Users/duffy.walsh@databricks.com/todaybank-loan-default")
print(f"    Run ID:      {champion.run_id}")
print(f"    Algorithm:   GradientBoostingClassifier (ProbaPredictor wrapper)")
print()
print("[3] MODEL REGISTRY (Unity Catalog)")
print(f"    Registered:  {MODEL_UC}")
print(f"    Version:     {champion.version}")
print(f"    Alias:       @champion")
print()
print("[4] SERVING ENDPOINT (Mosaic AI)")
print(f"    Endpoint:    {ENDPOINT}")
print(f"    Model:       {MODEL_UC} @champion v{champion.version}")
print(f"    API:         https://<workspace>/api/2.0/serving-endpoints/{ENDPOINT}/invocations")
print()
print("[5] SCORED OUTPUT")
print(f"    Table:       {CATALOG}.{SCHEMA}.loan_applications_scored")
print(f"    Rows:        {count:,}")
print(f"    Columns:     all features + pd_score + risk_tier + model_version + model_run_id")
print()
print("Lineage: loan_applications > MLflow run > UC Model Registry > serving endpoint > loan_applications_scored")
print()
print("Notebook 04 complete.")

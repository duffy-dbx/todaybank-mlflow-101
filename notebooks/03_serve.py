# Databricks notebook source
# MAGIC %md
# MAGIC # TodayBank Session 6 - Notebook 03: Create Serving Endpoint
# MAGIC
# MAGIC **Stage 03 RUN - Serve it, score it, watch it**
# MAGIC
# MAGIC This notebook:
# MAGIC 1. Creates a Mosaic AI Model Serving endpoint `todaybank-loan-default`
# MAGIC    (scale-to-zero, Small size, uses the prebuilt sklearn image)
# MAGIC 2. Waits until the endpoint is READY
# MAGIC 3. Tests a STRONG applicant (low default risk) vs a RISKY applicant (high risk)
# MAGIC
# MAGIC **Key concept for Axos:** A serving endpoint is a managed, versioned REST API.
# MAGIC The model version behind it is controlled by the `@champion` alias in UC - so
# MAGIC promoting a new model version is a single alias update, not an endpoint redeploy.

# COMMAND ----------

import time
import json
import requests
import mlflow
from mlflow import MlflowClient
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

CATALOG     = "todaybank_mlflow101"
MODEL_UC    = f"{CATALOG}.models.loan_default_risk"
ENDPOINT    = "todaybank-loan-default"

# Databricks workspace host + token
# spark.conf.get("spark.databricks.workspaceUrl") works in both interactive and job contexts
WORKSPACE_HOST = spark.conf.get("spark.databricks.workspaceUrl")
TOKEN          = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

HOST = f"https://{WORKSPACE_HOST}"
print(f"Workspace: {HOST}")
print(f"Endpoint name: {ENDPOINT}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 - Look up the @champion model version

# COMMAND ----------

client = MlflowClient()
model_version = client.get_model_version_by_alias(name=MODEL_UC, alias="champion")
print(f"Champion version: {model_version.version}  (registered model: {MODEL_UC})")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 - Create (or verify) the serving endpoint
# MAGIC
# MAGIC Configuration:
# MAGIC - `workload_size: Small` (1 replica)
# MAGIC - `scale_to_zero_enabled: true` (cost-efficient for demos)
# MAGIC - Uses the @champion alias so future model promotions auto-route here

# COMMAND ----------

ENDPOINT_CONFIG = {
    "name": ENDPOINT,
    "config": {
        "served_models": [
            {
                "model_name": MODEL_UC,
                "model_version": model_version.version,
                "workload_size": "Small",
                "scale_to_zero_enabled": True,
            }
        ]
    }
}

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

# Check if endpoint already exists
check_url = f"{HOST}/api/2.0/serving-endpoints/{ENDPOINT}"
r = requests.get(check_url, headers=headers)

if r.status_code == 200:
    existing = r.json()
    current_state = existing.get("state", {}).get("ready", "UNKNOWN")
    print(f"Endpoint already exists. State: {current_state}")
    if current_state == "READY":
        print("Endpoint is READY - no changes needed.")
    else:
        print("Endpoint exists but not READY - will wait for it.")
else:
    # Create the endpoint
    create_url = f"{HOST}/api/2.0/serving-endpoints"
    r_create = requests.post(create_url, headers=headers, json=ENDPOINT_CONFIG)
    print(f"Create response: {r_create.status_code}")
    if r_create.status_code not in (200, 201):
        print(r_create.text)
        raise RuntimeError(f"Failed to create endpoint: {r_create.text}")
    print("Endpoint creation started.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 - Wait for READY state
# MAGIC
# MAGIC Prebuilt sklearn image typically takes 10-15 minutes.
# MAGIC The notebook polls every 30 seconds and prints status updates.

# COMMAND ----------

MAX_WAIT_SEC = 1800  # 30 minutes max
POLL_INTERVAL = 30
waited = 0

print("Waiting for endpoint to reach READY state...")
while waited < MAX_WAIT_SEC:
    r = requests.get(f"{HOST}/api/2.0/serving-endpoints/{ENDPOINT}", headers=headers)
    state = r.json().get("state", {})
    ready  = state.get("ready", "UNKNOWN")
    config = state.get("config_update", "UNKNOWN")
    print(f"  [{waited:4d}s] ready={ready}  config_update={config}")
    if ready == "READY":
        print("\nEndpoint is READY. Waiting 30s for scale-up warmup before scoring...")
        time.sleep(30)  # brief warmup delay after READY (scale-to-zero warmup)
        break
    time.sleep(POLL_INTERVAL)
    waited += POLL_INTERVAL
else:
    raise TimeoutError(f"Endpoint did not reach READY within {MAX_WAIT_SEC} seconds.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 - Test the endpoint: STRONG applicant vs RISKY applicant
# MAGIC
# MAGIC **Strong applicant:** high credit score, low DTI, long employment, no prior delinquencies
# MAGIC **Risky applicant:** low credit score, high DTI, new employee, multiple delinquencies, debt consolidation

# COMMAND ----------

# Note: Mosaic AI serving invocations do NOT use the /api/2.0/ prefix
SCORE_URL = f"{HOST}/serving-endpoints/{ENDPOINT}/invocations"

def score_applicant(applicant_dict, label, max_retries=5, retry_delay=30):
    """
    Score a single applicant with retry logic.
    Retries handle brief scale-from-zero warmup periods where READY
    endpoints may still return 503 for the first few requests.
    """
    payload = {"dataframe_records": [applicant_dict]}
    for attempt in range(1, max_retries + 1):
        r = requests.post(SCORE_URL, headers=headers, json=payload)
        if r.status_code == 200:
            pd_score = r.json()["predictions"][0]
            risk_tier = "Low" if pd_score < 0.10 else ("High" if pd_score >= 0.30 else "Medium")
            print(f"\n--- {label} ---")
            print(f"  PD (probability of default): {pd_score:.4f}  ({pd_score*100:.1f}%)")
            print(f"  Risk tier: {risk_tier}")
            return pd_score
        else:
            print(f"  Attempt {attempt}/{max_retries} for {label}: HTTP {r.status_code}  {r.text[:200]}")
            if attempt < max_retries:
                time.sleep(retry_delay)
    raise RuntimeError(f"Scoring failed for {label} after {max_retries} attempts.")

# STRONG applicant
strong = {
    "credit_score": 780,
    "annual_income": 95000,
    "dti_ratio": 14.5,
    "loan_amount": 15000,
    "loan_term_months": 36,
    "interest_rate": 7.5,
    "employment_years": 12.0,
    "num_prior_delinquencies": 0,
    "home_ownership": "OWN",
    "loan_purpose": "home_improvement",
}

# RISKY applicant
risky = {
    "credit_score": 540,
    "annual_income": 32000,
    "dti_ratio": 48.0,
    "loan_amount": 25000,
    "loan_term_months": 60,
    "interest_rate": 21.0,
    "employment_years": 0.5,
    "num_prior_delinquencies": 3,
    "home_ownership": "RENT",
    "loan_purpose": "debt_consolidation",
}

pd_strong = score_applicant(strong, "STRONG applicant (low expected risk)")
pd_risky  = score_applicant(risky,  "RISKY applicant (high expected risk)")

# COMMAND ----------

print("\n=== Live scoring summary ===")
print(f"Strong applicant PD: {pd_strong:.4f}  ({pd_strong*100:.1f}%)")
print(f"Risky applicant PD:  {pd_risky:.4f}  ({pd_risky*100:.1f}%)")
if pd_risky is not None and pd_strong is not None:
    print(f"Separation:          {(pd_risky - pd_strong)*100:.1f} percentage points")
print(f"\nEndpoint: {ENDPOINT}  |  Model: {MODEL_UC}  @champion v{model_version.version}")
print("\nNotebook 03 complete.")

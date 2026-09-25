# TodayBank Session 6: MLflow & MLOps 101

**Series:** TodayBank Enablement - Session 6 of 6
**Use case:** Consumer Loan / Credit Default Risk
**Audience:** Zero-ML business stakeholders

---

## What this demo shows

The full ML lifecycle - training, tracking, registering, serving, and scoring a loan default
risk model - mapped to the Crawl / Walk / Run motif used across the TodayBank series:

| Stage | Activity | Databricks capability |
|---|---|---|
| CRAWL | Train + Track | MLflow experiment tracking |
| WALK | Register + Govern | MLflow Model Registry in Unity Catalog |
| RUN | Serve + Monitor | Mosaic AI Model Serving + batch scoring |

A `ProbaPredictor` wrapper returns continuous Probability of Default (PD) scores
instead of binary 0/1 labels, using the prebuilt sklearn serving image for fast
endpoint startup.

## Architecture

```
todaybank_mlflow101.lending.loan_applications (10,000 rows, labeled)
  |
  v
[Notebook 02] GradientBoosting (3 MLflow runs, best AUC-ROC selected)
  |
  v
todaybank_mlflow101.models.loan_default_risk @champion
  |
  +---> [Notebook 03] Serving endpoint: todaybank-loan-default
  |       - Real-time scoring via REST API
  |       - Scale-to-zero, Small
  |
  +---> [Notebook 04] Batch scoring
          |
          v
        todaybank_mlflow101.lending.loan_applications_scored (200 rows, PD + risk tier)
```

## Workspace

- **Host:** https://adb-7405619514730982.2.azuredatabricks.net
- **Profile:** wb-genie-demo
- **Catalog:** todaybank_mlflow101
  - Schema **lending**: loan_applications, new_applications, loan_applications_scored
  - Schema **models**: loan_default_risk (registered model)
- **Endpoint:** todaybank-loan-default
- **Experiment:** /Users/duffy.walsh@databricks.com/todaybank-loan-default

## How to run

### One-time deploy (from scratch)

```bash
chmod +x setup.sh teardown.sh
./setup.sh
```

The setup script:
1. Creates catalog todaybank_mlflow101 with explicit storage root (avoids serverless metastore error)
2. Creates schemas lending + models
3. Imports notebooks to workspace
4. Runs 01 > 02 > 03 > 04 sequentially, waiting for each
5. Verifies endpoint state

### Manual step-by-step

If you prefer to run notebooks interactively:

1. Open workspace https://adb-7405619514730982.2.azuredatabricks.net
2. Navigate to /Users/duffy.walsh@databricks.com/todaybank-mlflow-101/
3. Run notebooks in order: 01 > 02 > 03 > 04
4. Run each on Serverless or a small 1-worker cluster (DBR 15.4+)

### Serving endpoint test

```bash
# Get auth token
TOKEN=$(databricks auth token --profile wb-genie-demo | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Score a strong applicant
curl -s -X POST \
  https://adb-7405619514730982.2.azuredatabricks.net/serving-endpoints/todaybank-loan-default/invocations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dataframe_records": [{"credit_score": 780, "annual_income": 95000, "dti_ratio": 14.5, "loan_amount": 15000, "loan_term_months": 36, "interest_rate": 7.5, "employment_years": 12.0, "num_prior_delinquencies": 0, "home_ownership": "OWN", "loan_purpose": "home_improvement"}]}'
```

## Teardown

```bash
# Remove endpoint + model + schemas (keep catalog)
./teardown.sh

# Also drop the catalog (all data)
./teardown.sh --drop-catalog
```

## Local files

```
todaybank-mlflow-101/
  DEMO.md                    - Authoritative spec
  README.md                  - This file
  SETUP.md                   - Abstracted rebuild instructions (portable)
  setup.sh                   - Idempotent deploy script
  teardown.sh                - Cleanup script
  notebooks/
    01_generate_and_load.py  - Generate + write loan tables
    02_train_track_register.py - Train 3 runs, register @champion
    03_serve.py              - Create + wait for serving endpoint, test
    04_score_and_monitor.py  - Batch score + lineage summary
```

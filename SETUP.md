# SETUP.md - Build from Scratch (Portable)

Parameterized rebuild instructions for TodayBank Session 6: MLflow & MLOps 101.
Point at any workspace + catalog and rebuild without editing notebooks.

---

## Parameters

| Parameter | This demo's value | Your value |
|---|---|---|
| `WORKSPACE_HOST` | https://adb-7405619514730982.2.azuredatabricks.net | Your workspace URL |
| `PROFILE` | wb-genie-demo | Your Databricks CLI profile |
| `CATALOG` | todaybank_mlflow101 | Your catalog name |
| `STORAGE_ROOT` | abfss://unity-catalog-storage@dbstorage4srjorf5lmdx6.dfs.core.windows.net/7405619514730982/todaybank_mlflow101 | Your metastore storage path |
| `WAREHOUSE_ID` | 22b7cf4bfffde7dc | Your serverless SQL warehouse ID |
| `NOTEBOOK_WORKSPACE_PATH` | /Users/duffy.walsh@databricks.com/todaybank-mlflow-101 | Your workspace path |
| `EXPERIMENT_PATH` | /Users/duffy.walsh@databricks.com/todaybank-loan-default | Your MLflow experiment path |
| `ENDPOINT_NAME` | todaybank-loan-default | Your endpoint name |
| `REGISTERED_MODEL` | todaybank_mlflow101.models.loan_default_risk | Your 3-level model name |

---

## Step 0 - Prerequisites

1. Databricks CLI installed: `pip install databricks-cli` or `brew install databricks`
2. Authenticated profile in `~/.databrickscfg` (or run `databricks configure --profile <name>`)
3. Your user needs:
   - `CREATE CATALOG` privilege on the metastore
   - `USE CATALOG`, `CREATE SCHEMA`, `CREATE TABLE` on the new catalog
   - `CAN USE` on a serverless SQL warehouse
   - Cluster creation permission (for notebook runs)
   - `CAN MANAGE` on serving endpoints (for endpoint creation in notebook 03)

---

## Step 1 - Identify the metastore storage root

```bash
# Get metastore metadata
databricks metastores summary --profile <PROFILE>
# Look for: storage_root field
# Or check an existing managed catalog:
databricks catalogs get <any_existing_catalog> --profile <PROFILE>
# The storage_root follows this pattern:
# abfss://<container>@<storage_account>/<workspace_id>/<catalog_name>
```

For FEVM Azure workspaces the container is almost always `unity-catalog-storage`.

---

## Step 2 - Create the catalog via CLI

```bash
# REQUIRED: use --storage-root to avoid "Metastore storage root URL does not exist"
# error that occurs when creating catalogs from serverless notebooks
databricks catalogs create <CATALOG> \
  --storage-root "<STORAGE_ROOT>" \
  --comment "Your catalog description" \
  --profile <PROFILE>
```

---

## Step 3 - Create schemas

```bash
databricks schemas create lending <CATALOG> --profile <PROFILE>
databricks schemas create models  <CATALOG> --profile <PROFILE>
```

---

## Step 4 - Update notebook references

The 4 notebooks use hardcoded paths for the catalog, experiment path, and (in notebook 03)
the workspace host. Before importing, update these constants:

**All notebooks:** `CATALOG = "todaybank_mlflow101"` - change to your catalog name.

**Notebook 02 only:** `EXPERIMENT_PATH = "/Users/duffy.walsh@databricks.com/todaybank-loan-default"`
  - Change to your user path.

**Notebook 03 only:** No change needed - `WORKSPACE_HOST` is pulled from `dbutils` at runtime.

**Notebook 04 only:** `MODEL_UC = f"{CATALOG}.models.loan_default_risk"` - inherits CATALOG.

---

## Step 5 - Import notebooks

```bash
WORKSPACE_PATH="/Users/<your-username>@databricks.com/<your-folder>"

databricks workspace mkdirs "$WORKSPACE_PATH" --profile <PROFILE>

for NB in 01_generate_and_load 02_train_track_register 03_serve 04_score_and_monitor; do
  databricks workspace import "${WORKSPACE_PATH}/${NB}" \
    --file "notebooks/${NB}.py" \
    --language PYTHON --format SOURCE --overwrite \
    --profile <PROFILE>
done
```

---

## Step 6 - Run notebooks in order

Run each notebook on **Serverless** compute (preferred) or a small classic cluster
(1 worker, DBR 15.4+, Standard_DS3_v2 or equivalent). Wait for each to succeed.

Order: 01 > 02 > 03 > 04

Notebook 03 creates the serving endpoint and waits up to 30 minutes for READY state.
Prebuilt sklearn image typically takes 10-15 minutes.

---

## Step 7 - Verify

```bash
# 1. Endpoint state
databricks serving-endpoints get <ENDPOINT_NAME> --profile <PROFILE>
# Look for: "state": {"ready": "READY"}

# 2. Row counts (via SQL warehouse or notebook)
# SELECT COUNT(*) FROM <CATALOG>.lending.loan_applications         -- ~10000
# SELECT COUNT(*) FROM <CATALOG>.lending.new_applications          -- ~200
# SELECT COUNT(*) FROM <CATALOG>.lending.loan_applications_scored  -- ~200

# 3. Model alias
databricks registered-models get-by-alias \
  --full-name <REGISTERED_MODEL> --alias champion --profile <PROFILE>
```

---

## Step 8 - Teardown

```bash
# Delete serving endpoint
databricks serving-endpoints delete <ENDPOINT_NAME> --profile <PROFILE>

# Delete registered model (all versions)
databricks registered-models delete --full-name <REGISTERED_MODEL> --profile <PROFILE>

# Drop schemas
databricks schemas delete <CATALOG>.lending --profile <PROFILE>
databricks schemas delete <CATALOG>.models  --profile <PROFILE>

# Drop catalog (optional)
databricks catalogs delete <CATALOG> --force --profile <PROFILE>
```

---

## Known gotchas

1. **CREATE CATALOG on serverless fails** with "Metastore storage root URL does not exist".
   Always use `databricks catalogs create --storage-root` from the CLI, not SQL.

2. **MLflow log_model on serverless:** use `artifact_path=` not `name=`.

3. **Custom pyfunc serving hangs.** Log with the native sklearn flavor via the
   `ProbaPredictor` wrapper (predict() returns predict_proba(X)[:,1]).
   Avoids slow custom container builds; uses prebuilt sklearn image (~13 min deploy).

4. **REST serving endpoint invocation** expects `dataframe_records` format.
   The `pyfunc_predict_fn` field in the endpoint config is silently ignored -
   the ProbaPredictor wrapper's predict() is what determines the output format.

5. **Serving invocations URL does NOT use /api/2.0/ prefix.**
   Correct: `https://<workspace>/serving-endpoints/<name>/invocations`
   Wrong:   `https://<workspace>/api/2.0/serving-endpoints/<name>/invocations`

6. **Scale-to-zero cold start.** After the endpoint shows READY, the first
   scoring call may fail with 503 if the serving container has scaled to zero.
   Use retry logic (5 attempts, 30s delay) in any notebook that scores on
   first use after a READY transition.

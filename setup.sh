#!/usr/bin/env bash
# setup.sh - Idempotent deploy for TodayBank Session 6: MLflow & MLOps 101
# Usage: ./setup.sh [--profile <profile>]
# Default profile: wb-genie-demo
# Workspace: https://adb-7405619514730982.2.azuredatabricks.net

set -euo pipefail

# ---- Config ----
PROFILE="${1:-wb-genie-demo}"
if [[ "${1:-}" == "--profile" ]]; then
  PROFILE="${2:-wb-genie-demo}"
fi
WORKSPACE_HOST="https://adb-7405619514730982.2.azuredatabricks.net"
CATALOG="todaybank_mlflow101"
STORAGE_ROOT="abfss://unity-catalog-storage@dbstorage4srjorf5lmdx6.dfs.core.windows.net/7405619514730982/todaybank_mlflow101"
WAREHOUSE_ID="22b7cf4bfffde7dc"
NOTEBOOK_DIR="/Users/duffy.walsh@databricks.com/todaybank-mlflow-101"
LOCAL_NOTEBOOK_DIR="$(dirname "$0")/notebooks"

echo "========================================"
echo " TodayBank MLflow 101 - Setup"
echo " Profile: $PROFILE"
echo " Catalog: $CATALOG"
echo "========================================"

# ---- 1. Create catalog (skip if exists) ----
echo ""
echo "[1/6] Ensuring catalog $CATALOG exists..."
if databricks catalogs get "$CATALOG" --profile "$PROFILE" >/dev/null 2>&1; then
  echo "  Catalog already exists - skipping."
else
  echo "  Creating catalog with storage root..."
  databricks catalogs create "$CATALOG" \
    --storage-root "$STORAGE_ROOT" \
    --comment "TodayBank MLflow 101 demo - loan default risk MLOps (Session 6)" \
    --profile "$PROFILE"
  echo "  Catalog created."
fi

# ---- 2. Create schemas ----
echo ""
echo "[2/6] Ensuring schemas exist..."
for SCHEMA in lending models; do
  if databricks schemas get "${CATALOG}.${SCHEMA}" --profile "$PROFILE" >/dev/null 2>&1; then
    echo "  Schema ${CATALOG}.${SCHEMA} already exists - skipping."
  else
    echo "  Creating schema ${SCHEMA}..."
    if [ "$SCHEMA" = "lending" ]; then
      databricks schemas create "$SCHEMA" "$CATALOG" \
        --comment "TodayBank loan application data - loan default risk demo" \
        --profile "$PROFILE"
    else
      databricks schemas create "$SCHEMA" "$CATALOG" \
        --comment "TodayBank registered model registry - loan default risk" \
        --profile "$PROFILE"
    fi
    echo "  Schema ${SCHEMA} created."
  fi
done

# ---- 3. Import notebooks ----
echo ""
echo "[3/6] Importing notebooks..."
databricks workspace mkdirs "$NOTEBOOK_DIR" --profile "$PROFILE" 2>/dev/null || true

for NB in 01_generate_and_load 02_train_track_register 03_serve 04_score_and_monitor; do
  echo "  Importing $NB..."
  databricks workspace import \
    "${NOTEBOOK_DIR}/${NB}" \
    --file "${LOCAL_NOTEBOOK_DIR}/${NB}.py" \
    --language PYTHON \
    --format SOURCE \
    --overwrite \
    --profile "$PROFILE"
done
echo "  Notebooks imported."

# ---- Helper: submit and wait for a notebook run ----
get_token() {
  databricks auth token --profile "$PROFILE" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['access_token'])"
}

run_notebook() {
  local NB_PATH="$1"
  local RUN_NAME="$2"
  local TOKEN
  TOKEN=$(get_token)

  echo "  Submitting: $RUN_NAME"
  RESPONSE=$(curl -s -X POST \
    "${WORKSPACE_HOST}/api/2.1/jobs/runs/submit" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{
      \"run_name\": \"${RUN_NAME}\",
      \"tasks\": [{
        \"task_key\": \"run_notebook\",
        \"notebook_task\": {
          \"notebook_path\": \"${NB_PATH}\"
        },
        \"new_cluster\": {
          \"spark_version\": \"15.4.x-scala2.12\",
          \"node_type_id\": \"Standard_DS3_v2\",
          \"num_workers\": 1
        }
      }]
    }")

  RUN_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['run_id'])")
  echo "  Run ID: $RUN_ID  Waiting..."

  # Poll until terminal state
  while true; do
    sleep 30
    TOKEN=$(get_token)
    STATE_RESP=$(curl -s "${WORKSPACE_HOST}/api/2.1/jobs/runs/get?run_id=${RUN_ID}" \
      -H "Authorization: Bearer ${TOKEN}")
    LIFECYCLE=$(echo "$STATE_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['state']['life_cycle_state'])")
    RESULT_S=$(echo "$STATE_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['state'].get('result_state',''))")
    echo "    ... $LIFECYCLE / $RESULT_S"
    if [[ "$LIFECYCLE" = "TERMINATED" || "$LIFECYCLE" = "INTERNAL_ERROR" || "$LIFECYCLE" = "SKIPPED" ]]; then
      if [[ "$RESULT_S" != "SUCCESS" ]]; then
        echo "  ERROR: Notebook $RUN_NAME ended with $RESULT_S"
        exit 1
      fi
      echo "  SUCCESS: $RUN_NAME"
      return 0
    fi
  done
}

# ---- 4. Run notebooks sequentially ----
echo ""
echo "[4/6] Running notebooks (sequential, wait for each)..."
echo "  Note: cluster start adds ~5 min per run"

run_notebook "${NOTEBOOK_DIR}/01_generate_and_load"   "mlflow101-01-generate"
run_notebook "${NOTEBOOK_DIR}/02_train_track_register" "mlflow101-02-train"
run_notebook "${NOTEBOOK_DIR}/03_serve"                "mlflow101-03-serve"
run_notebook "${NOTEBOOK_DIR}/04_score_and_monitor"    "mlflow101-04-score"

# ---- 5. Verify tables ----
echo ""
echo "[5/6] Verifying tables..."
TOKEN=$(get_token)

# Row count check via jobs API would need another run; just echo instructions
echo "  Tables to verify manually or via SQL warehouse:"
echo "    SELECT COUNT(*) FROM ${CATALOG}.lending.loan_applications         -- expect ~10000"
echo "    SELECT COUNT(*) FROM ${CATALOG}.lending.new_applications          -- expect ~200"
echo "    SELECT COUNT(*) FROM ${CATALOG}.lending.loan_applications_scored  -- expect ~200"

# ---- 6. Verify endpoint ----
echo ""
echo "[6/6] Verifying serving endpoint..."
ENDPOINT_STATE=$(databricks serving-endpoints get todaybank-loan-default --profile "$PROFILE" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('state',{}).get('ready','UNKNOWN'))" 2>/dev/null || echo "NOT_FOUND")
echo "  Endpoint todaybank-loan-default state: $ENDPOINT_STATE"

echo ""
echo "========================================"
echo " Setup complete."
echo " Endpoint: todaybank-loan-default"
echo " Catalog:  ${CATALOG}.lending / ${CATALOG}.models"
echo "========================================"

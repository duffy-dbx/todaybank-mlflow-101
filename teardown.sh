#!/usr/bin/env bash
# teardown.sh - Remove TodayBank MLflow 101 demo resources
# Usage: ./teardown.sh [--profile <profile>] [--drop-catalog]
# Default profile: wb-genie-demo
# --drop-catalog: also deletes the catalog and all its data (IRREVERSIBLE)

set -euo pipefail

PROFILE="wb-genie-demo"
DROP_CATALOG=false

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile) PROFILE="$2"; shift 2 ;;
    --drop-catalog) DROP_CATALOG=true; shift ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

CATALOG="todaybank_mlflow101"
MODEL_UC="${CATALOG}.models.loan_default_risk"
ENDPOINT="todaybank-loan-default"

echo "========================================"
echo " TodayBank MLflow 101 - Teardown"
echo " Profile: $PROFILE"
echo " Drop catalog: $DROP_CATALOG"
echo "========================================"

# ---- 1. Remove serving endpoint ----
echo ""
echo "[1] Deleting serving endpoint $ENDPOINT..."
if databricks serving-endpoints get "$ENDPOINT" --profile "$PROFILE" >/dev/null 2>&1; then
  databricks serving-endpoints delete "$ENDPOINT" --profile "$PROFILE"
  echo "  Endpoint deleted."
else
  echo "  Endpoint not found - skipping."
fi

# ---- 2. Delete registered model ----
echo ""
echo "[2] Deleting registered model $MODEL_UC..."
# Use CLI to delete model (removes all versions)
if databricks registered-models delete --full-name "$MODEL_UC" --profile "$PROFILE" >/dev/null 2>&1; then
  echo "  Registered model deleted."
else
  echo "  Registered model not found or already deleted - skipping."
fi

# ---- 3. Drop schemas (and tables) ----
echo ""
echo "[3] Dropping schemas..."
for SCHEMA in models lending; do
  echo "  Dropping schema ${CATALOG}.${SCHEMA}..."
  if databricks schemas delete "${CATALOG}.${SCHEMA}" --profile "$PROFILE" >/dev/null 2>&1; then
    echo "  Schema ${SCHEMA} dropped."
  else
    echo "  Schema ${SCHEMA} not found - skipping."
  fi
done

# ---- 4. Optionally drop catalog ----
if [ "$DROP_CATALOG" = true ]; then
  echo ""
  echo "[4] Dropping catalog $CATALOG (IRREVERSIBLE)..."
  databricks catalogs delete "$CATALOG" --profile "$PROFILE" --force
  echo "  Catalog dropped."
else
  echo ""
  echo "[4] Skipping catalog drop (pass --drop-catalog to remove)."
fi

# ---- 5. Optionally remove workspace notebooks ----
echo ""
echo "[5] Workspace notebooks remain at:"
echo "  /Users/duffy.walsh@databricks.com/todaybank-mlflow-101/"
echo "  Delete manually if desired:  databricks workspace delete /Users/duffy.walsh@databricks.com/todaybank-mlflow-101 --recursive --profile $PROFILE"

echo ""
echo "Teardown complete."

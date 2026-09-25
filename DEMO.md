# DEMO.md - TodayBank Session 6: MLflow & MLOps 101

Internal spec. Source of truth for every asset in this directory. Formatting rules:
no em-dashes (use en-dashes " - "); ASCII `>` and `<` for arrows.

## Series context

TodayBank is the fictional regulated all-digital bank used across the TodayBank 
enablement series. Session 6 follows:
- Session 1: Lakehouse + Medallion Architecture
- Session 2: Unity Catalog + Governance
- Session 3: Agentic Capabilities
- Session 4: Unity AI Gateway
- Session 5: Production GenAI Part 1 (Crawl/Walk/Run)
- **Session 6 (this): Machine Learning + MLOps with MLflow**

## Audience & objective

- **Audience:** TodayBank stakeholders with NO prior ML experience. This is
  an introduction to Databricks ML capabilities, not an advanced MLOps deep-dive.
- **Objective:** Demystify ML. Show that ML on Databricks is a governed, repeatable
  lifecycle - not a black box - and that MLflow + Unity Catalog are the system of
  record that make it trustworthy, explainable, and defensible.
- **Tone:** story- and UI-driven. Minimal code on screen. Every ML term defined in
  plain English before it is shown.
- **Duration:** 50 minutes (slides + a ~25-minute live showcase).

## Use case

**Loan / credit default risk** - most relevant as a lending-centric digital
bank, and the easiest ML concept to explain to a zero-ML audience. We predict the
probability that a consumer loan applicant will default (PD), then score a brand-new
application live on stage.

Framing note for every governance claim: the platform supports the bank's model-risk
obligations; control design and validation remain the bank's decisions. This is not a
compliance attestation.

## The ML lifecycle mapped to the series' Crawl / Walk / Run motif

| Stage | Series word | What happens | Databricks capability |
|---|---|---|---|
| 00 | Demo | Name the scenario: Loan Default Risk | - |
| 01 | CRAWL - Train & Track | Train a simple model; every experiment auto-logged | MLflow experiment tracking |
| 02 | WALK - Register & Govern | Promote the best model; version, alias, lineage | MLflow Model Registry in Unity Catalog |
| 03 | RUN - Serve & Monitor | Deploy behind a live endpoint; score in real time; watch for drift | Mosaic AI Model Serving + monitoring concept |

"MLOps" = the discipline of moving a model through that lifecycle reliably, safely,
and repeatably - the same change-management, audit, and approval gates the bank
already applies to any production system.

## Scope (locked)

Lean intro. IN scope: experiment tracking, Model Registry in UC, real-time serving,
monitoring concept + lineage. OUT of scope (deliberately, for this audience): no
Streamlit app, no Unity AI Gateway, no champion/challenger MRM machinery. Keep it
approachable.

## Deployment target

- Workspace: FEVM **wb-genie-demo** = `https://adb-7405619514730982.2.azuredatabricks.net`
  (profile `wb-genie-demo`; FEVM deployment "todaybank-genai-demo"). 14-day TTL
  extension requested (ext id fd8aeb2c-e289-45cd-b352-6aaae112ef93).
- **New catalog** (per request): `todaybank_mlflow101`, schemas `.lending` (data)
  and `.models` (registered model). Serverless everywhere; UC 3-level namespaces;
  UC volumes only (no DBFS).

### Known workspace gotchas (carry into every worker prompt)

1. **New-catalog metastore storage-root error.** `CREATE CATALOG` on serverless
   notebooks fails with "Metastore storage root URL does not exist". Fix: create the
   catalog via CLI with an explicit `--storage-root`. On this workspace the pattern is
   `abfss://unity-catalog-storage@dbstorage4srjorf5lmdx6.dfs.core.windows.net/7405619514730982/todaybank_mlflow101`.
   VERIFY the metastore's default storage root during recon before hardcoding
   (`databricks metastores summary`), then create schemas via SQL warehouse.
2. **Serverless MLflow:** `mlflow.sklearn.log_model` wants `artifact_path=`, not `name=`.
3. **Custom pyfunc models hang on serving here** (DEPLOYMENT_CREATING >30 min then
   fail - slow custom-container build). Use the native sklearn flavor on the prebuilt
   image. To return probabilities, log a small `ProbaPredictor` sklearn wrapper whose
   `predict()` returns `predict_proba(X)[:, 1]` (the REST serving API silently drops
   `pyfunc_predict_fn`, so the wrapper - not the endpoint field - is what makes it work).

## Synthetic data (generated in-notebook, self-contained)

Consumer loan portfolio for TodayBank. In-notebook generation (numpy/pandas) so the
build needs no local Python env and reproduces anywhere.

- `todaybank_mlflow101.lending.loan_applications` - ~10,000 historical loans, LABELED
  with `defaulted` (target). Base default rate ~7-8%. Signal is realistic but learnable.
- `todaybank_mlflow101.lending.new_applications` - ~200 fresh, UNLABELED applications
  to score live and in batch.
- Features (plain-English, relatable): `credit_score`, `annual_income`, `dti_ratio`
  (debt-to-income), `loan_amount`, `loan_term_months`, `interest_rate`,
  `employment_years`, `num_prior_delinquencies`, `home_ownership`, `loan_purpose`.
- Produced by the pipeline: `loan_applications_scored` - new applications with model
  PD + a risk tier (Low/Medium/High).

## Notebooks (all serverless, heavily commented for narration)

| # | Notebook | What it does | Series stage |
|---|---|---|---|
| 01 | `01_generate_and_load` | Generate synthetic loans in-notebook; write labeled + new-application tables to UC | setup |
| 02 | `02_train_track_register` | Feature prep; train 3 MLflow-tracked runs (vary a couple of hyperparameters); compare runs in the UI; register the best model to UC Model Registry with `@champion` alias | 01 CRAWL |
| 03 | `03_serve` | Create Mosaic AI serving endpoint `todaybank-loan-default` (ProbaPredictor wrapper, prebuilt image, scale-to-zero, Small); wait READY; test a strong applicant vs a risky applicant | 03 RUN |
| 04 | `04_score_and_monitor` | Batch score `new_applications` > `loan_applications_scored` (PD + risk tier); show the inference/monitoring concept and end-to-end lineage source > model > endpoint > scored output | 02 WALK / 03 RUN |

The registry / governance story (Session stage 02 WALK) is narrated from the UC
Model Registry UI and the lineage graph, not a separate notebook.

## Deliverables (all in this directory)

1. `README.md` - overview, architecture, how to run, teardown.
2. `agenda.md` - the 50-minute agenda.
3. `SETUP.md` - abstracted, build-from-scratch instructions (parameterized so anyone
   can point at their own workspace + catalog and rebuild).
4. `setup.sh` - idempotent deploy (catalog, schemas, import + run notebooks, verify).
5. `teardown.sh` - remove endpoint, model, schema, and optionally the catalog.
6. `talk_track.md` - CLICK / SHOW / SAY cadence for the ~25-min live showcase,
   authored AFTER the notebooks are verified so the clicks are real.
7. `notebooks/` - 01-04 above.
8. `deck/` - 10-slide Google Slides deck in the Session 5 visual language + outline.

## Deck (Google Slides, Session 5 visual language)

Follow the style guide in `_styleguide/style-guide.md` exactly. DM Sans only; red
`#ff5f46` as the ONLY accent; deep teal `#0b2026` for dark section dividers and
column-header fills; slate `#475568` for secondary body; Databricks footer. 10-slide
arc mirroring Session 5:

1. Title - "Session 6: Databricks + Machine Learning & MLOps" + Duffy Walsh (SA),
   Kevin Collin (AE).
2. Forward-looking statement (reuse Session 5 boilerplate verbatim).
3. Agenda - "Built upon the foundations of previous sessions" (list Sessions 1-5) +
   "Where we are going" (MLflow tracking, Model Registry in UC, Mosaic AI serving,
   monitoring).
4. Journey diagram (three-column) - the ML lifecycle as Crawl > Walk > Run:
   CRAWL = Train + Track (MLflow experiments); WALK = Register + Govern (UC Model
   Registry); RUN = Serve + Monitor (Mosaic AI Model Serving).
5. 00 - Demo - "Loan Default Risk Model".
6. 01 - CRAWL - "Train once, track everything".
7. 02 - WALK - "One governed model registry".
8. 03 - RUN - "Serve it, score it, watch it".
9. Where a Bank Gets Value - business outcomes (below).
10. Q & A.

Value bullets (slide 9): a trustworthy, auditable model-risk story from day one;
every experiment reproducible for examiners; one governed model registry in UC;
real-time credit decisions behind a managed endpoint; the same lifecycle pattern for
every future model (fraud, churn, marketing).

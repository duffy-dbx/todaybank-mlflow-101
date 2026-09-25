# TodayBank (Axos) Session 6: MLflow & MLOps 101 - Demo Agenda (50 min)

**Audience:** Axos / TodayBank stakeholders with no prior ML experience. This is an
introduction to Databricks ML capabilities.
**Duration:** 50 minutes (slides + a ~25-minute live showcase on Databricks).
**Objective:** Demystify ML. Show that ML on Databricks is a governed, repeatable
lifecycle - not a black box - and that MLflow + Unity Catalog are the system of record
that make a prediction trustworthy, explainable, and defensible.

> Framing note: this session shows how the platform's controls support the bank's
> model-risk obligations. It is not a compliance attestation - control design and
> validation remain the bank's decisions.

## At a glance

| Time | Segment | Format |
|---|---|---|
| 0-5 | 1. Why this matters for a digital bank | Slide |
| 5-10 | 2. The ML lifecycle in plain English | Slide (Crawl/Walk/Run) |
| 10-15 | 3. Where this builds on Sessions 1-5 | Slide |
| 15-42 | 4. Live showcase - the loan default model | Live on Databricks (~25 min) |
| 42-50 | 5. Where Axos gets value + Q&A | Discussion |

## 1. Why this matters for a digital bank (5 min)
- Anchor on decisions Axos makes every day: who to lend to, at what rate. The core
  question: "How do we make a prediction we can trust, explain, and defend to an
  examiner?"
- Plain-English framing: "ML just learns patterns from your own history to predict the
  next outcome. MLOps is how you do that reliably, safely, and repeatably - the same way
  you run any production system."

## 2. The ML lifecycle in plain English (5 min)
- One slide, the Crawl > Walk > Run motif from the series:
  - CRAWL - Train & Track: build a model; capture every experiment.
  - WALK - Register & Govern: promote the best model into one governed registry.
  - RUN - Serve & Monitor: put it behind a live endpoint; score in real time; watch it.
- Map each stage to a control the bank already understands: change management, audit
  trail, approval gates.

## 3. Where this builds on Sessions 1-5 (5 min)
- Same governed Lakehouse on Unity Catalog. The model reads the same governed tables;
  the model itself becomes a governed UC asset with the same permissions and lineage.
- No separate ML stack to secure. One platform, one governance layer.

## 4. Live showcase - the loan default model (25 min)
- **00 Demo (2 min)** - name the scenario: predict a consumer loan applicant's
  probability of default.
- **01 CRAWL - Train & Track (8 min)** - train a simple model in a notebook; MLflow
  auto-logs params, metrics, and the model artifact; compare a few runs side by side.
  Message: nothing is lost, every experiment is reproducible and auditable.
- **02 WALK - Register & Govern (7 min)** - register the winning model to the Unity
  Catalog Model Registry; show versions, the `@champion` alias, and lineage back to the
  training data. Message: the model inherits the same governance as your data.
- **03 RUN - Serve & Monitor (8 min)** - deploy to a Mosaic AI serving endpoint; score
  a strong applicant vs a risky applicant live; batch-score a fresh application set;
  show the inference/monitoring concept for drift. Message: from experiment to a
  production credit-decision API, governed end to end.

## 5. Where Axos gets value + next steps (8 min)
- A trustworthy, auditable model-risk story from day one; one governed model registry;
  real-time decisions behind a managed endpoint; the same lifecycle pattern reused for
  every future model (fraud, churn, marketing).
- Proposed follow-ups: a scoped hands-on POC on Axos data; a model-inventory /
  governance walkthrough.

## Prep checklist (internal - not for the customer)
- Confirm attendee roles; keep every ML term defined in plain English before showing it.
- Verify endpoint is READY and warehouse is running before the session; have
  screenshots as a fallback for any live step (serving cold-start can take a minute).
- Use synthetic loan data only; never show real borrower data.

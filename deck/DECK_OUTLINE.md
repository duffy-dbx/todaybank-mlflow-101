# Deck Outline - Axos Bank Session 6: Machine Learning & MLOps with MLflow

**Presentation URL:** https://docs.google.com/presentation/d/13-f61bpbcV-SIzCNgq-QD5pVn0tsgJLzpKnLnwOpjgc/edit

**Presenters:** Duffy Walsh (Solutions Architect), Kevin Collin (Enterprise Account Executive)

**Style:** Session 5 visual language - DM Sans, #ff5f46 accent, #0b2026 teal dark, 13.333" x 7.5"

---

## Slide 1 - Title Slide

**Layout:** Title (light background, session 5 master with decorative shapes on right)

**Heading:**
Session 6: Databricks + Machine Learning & MLOps

**Presenter strip (bottom):**
- Duffy Walsh | Solutions Architect (name: red bold, role: slate)
- Kevin Collin | Enterprise Account Executive

**Speaker note stub:**
> All regulated FIs face growing AI and model complexity. Teams are building models in siloed notebooks, with no single view of what ran, what shipped, or what is currently serving traffic. Today we tell the story of how Databricks gives you a governed, reproducible, production-grade ML platform - using TodayBank as our fictional regulated bank stand-in.

---

## Slide 2 - Forward-looking Statement

**Layout:** Dense text / legal boilerplate

**Heading:** Forward-looking Statement (60pt)

**Body:** Standard Databricks safe-harbor text (verbatim from Session 5)

**Speaker note stub:**
> Standard safe-harbor. Today's demo mixes GA, Public Preview, and Beta capabilities - I will flag maturity as we go.

---

## Slide 3 - Agenda (Two-column)

**Layout:** Two-column with intro line

**Title:** Databricks + Machine Learning & MLOps

**Intro line:** Built upon the foundations of previous sessions:

**Left column (18pt regular):**
- Session 1: Lakehouse + Medallion Architecture
- Session 2: Unity Catalog + Governance
- Session 3: Agentic Capabilities
- Session 4: Unity AI Gateway
- Session 5: Production GenAI Part 1

**Right column (20pt bold - "Where we are going:"):**
- MLflow experiment tracking
- Model Registry in Unity Catalog
- Mosaic AI Model Serving
- Model monitoring

**Speaker note stub:**
> We have built the governed data foundation. Today we wire up the ML lifecycle on top of it. Every model TodayBank builds will inherit the same access controls, lineage, and audit trail they already have for data. The hard part is done.

---

## Slide 4 - Journey Diagram (Crawl > Walk > Run)

**Layout:** Three-column diagram (hand-built rectangles + text)

**Title:** The ML Lifecycle: Crawl > Walk > Run (30pt, dark teal)

**Subtitle (red):** From a notebook experiment to a governed, real-time credit decision

**Three-column diagram:**

| CRAWL | > | WALK | > | RUN |
|-------|---|------|---|-----|
| Train & Track | | Register & Govern | | Serve & Monitor |
| MLflow experiment tracking | | Model Registry in Unity Catalog | | Mosaic AI Model Serving |
| Every run auto-logged | | Versioned, aliased, lineage | | Real-time score + drift watch |

**Speaker note stub:**
> This is the arc we will walk today. Crawl is just a notebook with MLflow autolog - zero new infrastructure. Walk is where we move from "it ran" to "it is governed" - registered, versioned, and aliased in Unity Catalog. Run is the production gate: evaluated, served, observable, and traced. Each stage delivers standalone value; you can stop at any.

---

## Slide 5 - Section Divider "00 Demo"

**Layout:** Dark section divider (background: #0b2026, thin red bar at top)

**Step number:** 00 (red, 35pt bold)

**Hero word:** Demo (white, 107pt bold)

**Subtitle (italic, off-white):** Loan Default Risk Model

**Speaker note stub:**
> This demo uses a fictional TodayBank credit risk scenario. We will build a LightGBM loan default probability model, track every experiment in MLflow, register the winning version in Unity Catalog's Model Registry, and serve it behind a managed endpoint with AI Gateway guardrails.

---

## Slide 6 - Section Divider "01 CRAWL"

**Layout:** Dark section divider

**Step number:** 01

**Hero word:** CRAWL

**Subtitle:** Train once, track everything

**Speaker note stub:**
> The Crawl phase is a training notebook with one line change: `mlflow.autolog()`. MLflow automatically captures hyperparameters, metrics (AUC, precision, recall), the model artifact, the data schema, and the environment. Every run is reproducible and searchable. No separate experiment tracking system needed - it is already there.

---

## Slide 7 - Section Divider "02 WALK"

**Layout:** Dark section divider

**Step number:** 02

**Hero word:** WALK

**Subtitle:** One governed model registry

**Speaker note stub:**
> Walk is where we graduate from "notebook experiment" to "governed asset." We register the best run in Unity Catalog's Model Registry. From this point the model has an alias (champion), a version, UC lineage back to the training data, and access control tied to TodayBank's existing UC permissions. A regulator can ask "what data trained your credit model?" and we can answer in seconds.

---

## Slide 8 - Section Divider "03 RUN"

**Layout:** Dark section divider

**Step number:** 03

**Hero word:** RUN

**Subtitle:** Serve it, score it, watch it

**Speaker note stub:**
> Run is the production gate. We use MLflow evaluate to measure model quality before shipping - bias metrics, calibration, confusion matrix. We deploy the champion alias behind a Mosaic AI Model Serving endpoint. AI Gateway applies rate limits, logs every inference, and the MLflow tracing surface gives us a call-by-call audit trail. If the model drifts, monitoring fires an alert before a regulator does.

---

## Slide 9 - Value Summary

**Layout:** Content with subtitle callout

**Title:** Where Axos Bank Gets Value (30pt)

**Callout (bold italic):** Production-grade means governed, auditable, and yours.

**Body (bullets):**
- A trustworthy, auditable model-risk story from day one
- Every experiment reproducible and examinable
- One governed model registry in Unity Catalog
- Real-time credit decisions behind a managed endpoint
- The same lifecycle pattern for every future model (fraud, churn, marketing)

**Speaker note stub:**
> This is not a one-off demo. The pattern we showed today - autolog, register, evaluate, serve, trace - applies to every model TodayBank will ever build. Fraud models, churn models, marketing propensity. Each one inherits the same governance, the same audit trail, and the same exam-ready paper trail automatically.

---

## Slide 10 - Q & A

**Layout:** Minimal closing (single large text, white background)

**Text:** Q & A (60pt, dark teal)

**Speaker note stub:**
> Proposed next step: a scoped pilot targeting the loan default risk use case in a controlled workspace. Define success criteria with model risk, agree on evaluation thresholds, and run one full Crawl - Walk - Run cycle. Timeline: 4 - 6 weeks.

---

## Build Notes

- Presentation created by copying Session 5 (to inherit correct 13.333" x 7.5" page size and DM Sans masters)
- All 10 slides cleared of Session 5 content and rebuilt from scratch
- Validation: PASS - 0 errors, 4 warnings (all expected/intentional)
  - S2: 60pt heading text-overflow - matches Session 5 design, single line renders fine
  - S4: 3x element-overlap - CRAWL/WALK/RUN rect+header text overlay is intentional
- Polish needed:
  - Slide 1: red decorative geometric shapes (triangle, circle, square) appear on the right half of the title slide. These are from the copied Session 5 title layout and match the original style. If you want a cleaner look, delete the geometric shapes manually in Google Slides by clicking each shape on the title slide and pressing Delete.
  - The deck has no images/diagrams - consider adding a MLflow UI screenshot or architecture diagram to slide 4 for live demo context.

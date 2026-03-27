# Phase 0 Research - CarbonCheck Trust Journeys

## Decision 1: Verification architecture baseline
- Decision: Adopt a four-layer engine module at `backend/verification_engine`: Ground Layer (registry and document truth), Satellite Layer (NDVI time-series), AI Layer (carbon estimate and anomaly detection), Scoring Layer (rule-based checks and final Trust Score/Verdict).
- Rationale: Matches starter-kit replacement objective while keeping concerns isolated and testable.
- Alternatives considered:
  - Extend current scoring service in-place: rejected due to tight coupling and weak traceability.
  - Merge AI and scoring into one layer: rejected because it hides explainability and breaks deterministic auditability.

## Decision 2: Ground Layer data acquisition strategy
- Decision: Use async registry clients (`httpx`) plus PDF extraction (`pdfplumber`, `beautifulsoup4`, `lxml`) to produce normalized `RegistryProject` and extraction records with provenance fields.
- Rationale: Registry data and project documents are complementary and required for robust evidence narratives.
- Alternatives considered:
  - Registry API only: rejected because key claims often exist only in supporting PDFs.
  - PDF scraping only: rejected due to weaker canonical project identity and metadata consistency.

## Decision 3: Satellite Layer provider and fallback
- Decision: Use Google Earth Engine as the primary satellite provider with bounded-call execution and cached NDVI fallbacks from Supabase when unavailable.
- Rationale: Earth Engine offers mature NDVI access and broad historical coverage needed for trend checks.
- Alternatives considered:
  - Local-only raster ingestion pipeline: rejected for MVP due to setup/operations overhead.
  - No satellite signal in MVP: rejected because it weakens fraud confidence and evidence quality.

## Decision 4: AI Layer model stack
- Decision: Use deterministic feature pipelines with model-backed estimates (`torch`/`torchgeo` for estimation support, `scikit-learn` and `pyod`/`xgboost` for anomaly scoring) and record model/version metadata per run.
- Rationale: Keeps AI useful while preserving repeatability and explainable traceability under fixed snapshots.
- Alternatives considered:
  - Pure heuristics without models: rejected because anomaly detection quality is insufficient for audit triage.
  - End-to-end black-box model: rejected due to low explainability and constitution risk.

## Decision 5: Scoring Layer contract and thresholds
- Decision: Keep four explicit checks with fixed scoring contributions and verdict mapping: FAIL `< 40`, WARNING `40-69`, PASS `>= 70`; emit `UNVERIFIED` when inputs are insufficient.
- Rationale: Stable, demo-friendly interpretation and deterministic outcomes across retries.
- Alternatives considered:
  - Dynamic thresholding by batch percentile: rejected due to non-determinism.
  - Binary pass/fail only: rejected because WARNING is essential for triage workflows.

## Decision 6: API shape for verification flow
- Decision: Preserve one canonical verify endpoint (`POST /api/verify`) supporting 1..50 IDs, and represent per-ID outputs with layered evidence summaries plus error isolation for invalid IDs.
- Rationale: One client contract minimizes frontend churn and keeps batch/single logic consistent.
- Alternatives considered:
  - Introduce separate v2 endpoint only: rejected for now to avoid temporary dual-contract complexity in the plan.

## Decision 7: Timeout, fallback, and freshness policy
- Decision: Enforce strict upstream time budgets, then degrade to cache snapshots with `data_mode` (`live|mixed|cache`) and `fallback_used` flags; never produce HTTP 500 from expected business paths.
- Rationale: Required for constitution reliability and demo continuity.
- Alternatives considered:
  - Fail closed on any upstream failure: rejected because it breaks core journey availability.
  - Omit freshness metadata in responses: rejected due to provenance requirement.

## Decision 8: Dependency adoption policy for MVP
- Decision: Integrate starter-kit dependencies in staged groups (core parsing, geospatial, AI) and gate heavyweight packages behind import boundaries and optional runtime checks where possible.
- Rationale: Avoids blocking deploy cycles while enabling progressive verification depth.
- Alternatives considered:
  - Add all packages as hard runtime requirements on day one: rejected because environment variance can destabilize demos.
  - Avoid new dependencies entirely: rejected because the requested architecture cannot be implemented credibly without them.

## Decision 9: Security and abuse controls
- Decision: Validate ID format early, enforce payload size/rate limits, constrain registry parameter values, and avoid logging sensitive raw payloads beyond request IDs and operational diagnostics.
- Rationale: Meets constitution guardrails with low implementation overhead.
- Alternatives considered:
  - Trust client-side validation only: rejected as bypassable.
  - Global-only throttling without endpoint policies: rejected as too coarse.

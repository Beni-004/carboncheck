# Phase 1 Data Model - CarbonCheck Trust Journeys

## Modeling Principles
- Layer traceability: each verification run captures Ground, Satellite, AI, and Scoring artifacts.
- Deterministic replay: same normalized input plus same source/model snapshots reproduces same score and verdict.
- API resilience: cached-source and degraded outcomes are first-class modeled states, not exceptional paths.

## Entity: credit_project (Ground Layer canonical record)

| Field | Type | Constraints | Notes |
|---|---|---|---|
| id | uuid | PK, default gen_random_uuid() | Internal key |
| project_id | text | NOT NULL, UNIQUE, CHECK length 3..128 | External credit ID |
| registry | text | NOT NULL, CHECK in ('verra','gold_standard','acr','other') | Source registry |
| project_name | text | NULL | Human-readable name |
| project_type | text | NOT NULL, CHECK in ('forestry','renewable','soil','other') | Risk grouping |
| methodology | text | NULL | Registry methodology code |
| vintage_year | int | NULL, CHECK between 1990 and 2100 | Used by satellite/AI windows |
| latitude | numeric(9,6) | NULL, CHECK between -90 and 90 | Geo anchor |
| longitude | numeric(9,6) | NULL, CHECK between -180 and 180 | Geo anchor |
| claimed_co2_tons | numeric(14,2) | NULL, CHECK >= 0 | Ground-truth claim |
| registry_url | text | NULL | Evidence source |
| fetched_at | timestamptz | NOT NULL | Last canonical fetch time |
| created_at | timestamptz | NOT NULL, default now() | Audit |
| updated_at | timestamptz | NOT NULL, default now() | Audit |

Indexes:
- idx_credit_project_registry_project_id (registry, project_id)
- idx_credit_project_type (project_type)

## Entity: source_snapshot (Ground/Satellite provenance)

| Field | Type | Constraints | Notes |
|---|---|---|---|
| id | uuid | PK, default gen_random_uuid() | Snapshot key |
| project_id | uuid | NOT NULL, FK -> credit_project(id) | Subject project |
| layer | text | NOT NULL, CHECK in ('ground','satellite') | Source layer |
| source_name | text | NOT NULL | Registry/API/cache identifier |
| fetched_at | timestamptz | NOT NULL | Source fetch time |
| freshness_state | text | NOT NULL, CHECK in ('live','cache','stale','mixed') | Provenance state |
| fallback_used | boolean | NOT NULL, default false | Whether cache substituted live source |
| snapshot_hash | text | NOT NULL | Determinism anchor material |
| payload_ref | text | NULL | Pointer to cached payload/blob |
| created_at | timestamptz | NOT NULL, default now() | Audit |

Indexes:
- idx_source_snapshot_project_layer (project_id, layer, created_at desc)
- idx_source_snapshot_hash (snapshot_hash)

## Entity: ai_inference (AI Layer outputs)

| Field | Type | Constraints | Notes |
|---|---|---|---|
| id | uuid | PK, default gen_random_uuid() | Inference key |
| project_id | uuid | NOT NULL, FK -> credit_project(id) | Subject project |
| ndvi_avg | numeric(6,4) | NULL | Aggregated vegetation signal |
| ndvi_trend | numeric(7,5) | NULL | Annualized trend |
| estimated_co2_tons | numeric(14,2) | NULL, CHECK >= 0 | AI estimate |
| uncertainty_pct | numeric(5,2) | NULL, CHECK between 0 and 100 | Model uncertainty |
| anomaly_score | numeric(6,4) | NULL | Outlier strength |
| anomaly_flag | boolean | NOT NULL, default false | Binary anomaly output |
| model_family | text | NOT NULL | e.g. torchgeo/xgboost/pyod |
| model_version | text | NOT NULL | Reproducibility control |
| feature_hash | text | NOT NULL | Determinism anchor material |
| inferred_at | timestamptz | NOT NULL | Inference timestamp |

Indexes:
- idx_ai_inference_project_time (project_id, inferred_at desc)
- idx_ai_inference_model_version (model_family, model_version)

## Entity: verification_run (Scoring Layer durable result)

| Field | Type | Constraints | Notes |
|---|---|---|---|
| id | uuid | PK, default gen_random_uuid() | Verification key |
| request_id | uuid | NOT NULL | Correlates API call |
| project_id | uuid | NOT NULL, FK -> credit_project(id) | Subject project |
| source_snapshot_hash | text | NOT NULL | Combined source determinism anchor |
| model_snapshot_hash | text | NULL | AI/model determinism anchor |
| trust_score | numeric(5,2) | NOT NULL, CHECK between 0 and 100 | Final score |
| verdict | text | NOT NULL, CHECK in ('FAIL','WARNING','PASS','UNVERIFIED') | User-facing decision |
| data_mode | text | NOT NULL, CHECK in ('live','mixed','cache') | Availability mode |
| fallback_used | boolean | NOT NULL, default false | Any fallback in execution |
| rank_in_batch | int | NULL, CHECK > 0 | Bulk-order value |
| error_code | text | NULL | Partial/terminal domain error code |
| created_at | timestamptz | NOT NULL, default now() | Audit |

Indexes:
- idx_verification_run_request (request_id)
- idx_verification_run_project_created (project_id, created_at desc)
- idx_verification_run_verdict_created (verdict, created_at desc)

## Entity: verification_check (Scoring Layer per-check evidence)

| Field | Type | Constraints | Notes |
|---|---|---|---|
| id | uuid | PK, default gen_random_uuid() | Check key |
| verification_run_id | uuid | NOT NULL, FK -> verification_run(id) ON DELETE CASCADE | Parent run |
| check_name | text | NOT NULL | e.g. carbon_overcrediting |
| passed | boolean | NOT NULL | Check pass/fail |
| points_awarded | int | NOT NULL, CHECK between 0 and 25 | Scoring contribution |
| severity | text | NOT NULL, CHECK in ('low','medium','high','critical') | Risk indicator |
| evidence_text | text | NOT NULL | Explainable evidence |

Unique constraint:
- UNIQUE (verification_run_id, check_name)

## Entity: leaderboard_snapshot (Public read model)

| Field | Type | Constraints | Notes |
|---|---|---|---|
| id | uuid | PK, default gen_random_uuid() | Snapshot entry key |
| snapshot_at | timestamptz | NOT NULL | Refresh timestamp |
| project_id | text | NOT NULL | Public identifier |
| project_type | text | NOT NULL, CHECK in ('forestry','renewable','soil','other') | Grouping |
| current_verdict | text | NOT NULL, CHECK in ('FAIL','WARNING','PASS','UNVERIFIED') | Display verdict |
| trust_score | numeric(5,2) | NOT NULL, CHECK between 0 and 100 | Display score |
| flagged_count_24h | int | NOT NULL, CHECK >= 0 | Trend signal |
| rank_overall | int | NOT NULL, CHECK > 0 | Global ranking |
| rank_by_type | int | NOT NULL, CHECK > 0 | Category ranking |
| freshness_state | text | NOT NULL, CHECK in ('fresh','stale','degraded') | Transparency badge |
| evidence_snippet | text | NOT NULL | Human-readable explanation |

Indexes:
- idx_leaderboard_snapshot_global (snapshot_at desc, rank_overall)
- idx_leaderboard_snapshot_type (snapshot_at desc, project_type, rank_by_type)

## Derived Validation Rules
- Verify request accepts exactly one mode:
  - single: one `project_id`
  - bulk: array `project_ids` length 1..50
- Invalid IDs produce per-item errors without failing valid IDs in the same batch.
- Verdict mapping:
  - FAIL: `trust_score < 40`
  - WARNING: `40 <= trust_score < 70`
  - PASS: `trust_score >= 70`
  - UNVERIFIED: required cross-layer evidence missing

## State Transitions
- Freshness lifecycle:
  - `live -> mixed` when one or more sources fallback
  - `mixed -> cache` when all sources served from cache
  - any state -> `live` when all sources recover
- Verification lifecycle:
  - `UNVERIFIED -> WARNING|FAIL|PASS` after sufficient evidence arrives
  - `PASS|WARNING|FAIL -> UNVERIFIED` if replay detects missing mandatory evidence under stricter policy

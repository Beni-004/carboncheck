# Phase 1 Data Model - CarbonCheck Trust Journeys

## Schema Principles
- Deterministic scoring snapshots: all score rows capture exact check values and source snapshot hash.
- Rigid constraints: strict enums, bounded ranges, non-nullable core fields, and uniqueness guarantees.
- Read optimization: leaderboard served from precomputed cache table.

## Table: carbon_credits
Canonical registry metadata plus source freshness references.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | uuid | PK, default gen_random_uuid() | Internal key |
| credit_id | text | NOT NULL, UNIQUE, CHECK (length(credit_id) between 3 and 128) | User-facing ID |
| project_name | text | NOT NULL | Credit project name |
| credit_type | text | NOT NULL, CHECK (credit_type in ('Forestry','Renewable','Soil')) | Leaderboard grouping |
| issuer | text | NOT NULL | Registry/issuer label |
| vintage_year | int | NOT NULL, CHECK (vintage_year between 1990 and 2100) | Domain bound |
| country_code | text | NOT NULL, CHECK (char_length(country_code)=2) | ISO-2 style |
| status | text | NOT NULL, CHECK (status in ('active','retired','suspended','unknown')) | Current lifecycle |
| source_embr_fetched_at | timestamptz | NULL | Latest Ember fetch |
| source_cea_fetched_at | timestamptz | NULL | Latest CEA fetch |
| source_grid_india_fetched_at | timestamptz | NULL | Latest Grid-India fetch |
| source_rec_registry_fetched_at | timestamptz | NULL | Latest REC Registry fetch |
| cache_stale_after | timestamptz | NOT NULL | Freshness threshold for fallback |
| created_at | timestamptz | NOT NULL, default now() | Audit |
| updated_at | timestamptz | NOT NULL, default now() | Audit |

Indexes:
- idx_carbon_credits_credit_type (credit_type)
- idx_carbon_credits_cache_stale_after (cache_stale_after)

## Table: trust_scores
Per-request deterministic output for one credit_id with full check breakdown.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | uuid | PK, default gen_random_uuid() | Internal key |
| request_id | uuid | NOT NULL | Correlates API request |
| carbon_credit_id | uuid | NOT NULL, FK -> carbon_credits(id) ON DELETE CASCADE | Subject credit |
| baseline_match | numeric(5,2) | NOT NULL, CHECK (baseline_match between 0 and 100) | Check score |
| additionality | numeric(5,2) | NOT NULL, CHECK (additionality between 0 and 100) | Check score |
| permanence_risk | numeric(5,2) | NOT NULL, CHECK (permanence_risk between 0 and 100) | Check score (higher is safer after normalization) |
| double_counting | numeric(5,2) | NOT NULL, CHECK (double_counting between 0 and 100) | Check score |
| trust_score | numeric(5,2) | NOT NULL, CHECK (trust_score between 0 and 100) | Weighted total |
| verdict | text | NOT NULL, CHECK (verdict in ('FAIL','WARNING','PASS','UNSCORED')) | User-visible class |
| rank_in_batch | int | NULL, CHECK (rank_in_batch > 0) | Present in bulk mode |
| data_mode | text | NOT NULL, CHECK (data_mode in ('live','mixed','cache')) | Provenance mode |
| fallback_used | boolean | NOT NULL, default false | Any source fallback occurred |
| source_snapshot_hash | text | NOT NULL | Determinism anchor |
| evidence_summary | text | NOT NULL | Explainability snippet |
| error_code | text | NULL | Domain error (never 500) |
| created_at | timestamptz | NOT NULL, default now() | Audit |

Indexes:
- idx_trust_scores_credit_created (carbon_credit_id, created_at desc)
- idx_trust_scores_request_id (request_id)
- idx_trust_scores_verdict_created (verdict, created_at desc)

## Table: leaderboard_cache
Public read model, refreshed by scheduler.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | uuid | PK, default gen_random_uuid() | Internal key |
| credit_id | text | NOT NULL | Denormalized for fast UI |
| credit_type | text | NOT NULL, CHECK (credit_type in ('Forestry','Renewable','Soil')) | Category |
| flagged_count_24h | int | NOT NULL, CHECK (flagged_count_24h >= 0) | Rolling indicator |
| avg_trust_score_24h | numeric(5,2) | NOT NULL, CHECK (avg_trust_score_24h between 0 and 100) | Trend signal |
| current_verdict | text | NOT NULL, CHECK (current_verdict in ('FAIL','WARNING','PASS','UNSCORED')) | Snapshot verdict |
| rank_global | int | NOT NULL, CHECK (rank_global > 0) | Overall rank |
| rank_by_type | int | NOT NULL, CHECK (rank_by_type > 0) | Per-category rank |
| evidence_snippet | text | NOT NULL | Public explanation |
| snapshot_at | timestamptz | NOT NULL | Cache build time |
| freshness_state | text | NOT NULL, CHECK (freshness_state in ('fresh','stale','degraded')) | Display label |

Constraints:
- UNIQUE (snapshot_at, credit_type, rank_by_type)
- UNIQUE (snapshot_at, rank_global)

Indexes:
- idx_leaderboard_cache_snapshot_type_rank (snapshot_at desc, credit_type, rank_by_type)
- idx_leaderboard_cache_snapshot_global_rank (snapshot_at desc, rank_global)

## Derived Rules
- Verdict mapping:
  - FAIL: trust_score < 40
  - WARNING: trust_score >= 40 and trust_score < 70
  - PASS: trust_score >= 70
- Weighted total:
  - trust_score = round((baseline_match*0.30 + additionality*0.25 + permanence_risk*0.25 + double_counting*0.20), 2)

## State Transitions
- carbon_credits.status:
  - unknown -> active|suspended|retired
  - active -> suspended|retired
  - suspended -> active|retired
  - retired -> retired (terminal)
- freshness_state in leaderboard_cache:
  - fresh -> stale when snapshot age exceeds SLA
  - stale -> degraded if one or more upstream sources unavailable in latest refresh
  - degraded -> fresh when all upstream sources healthy and refresh succeeds

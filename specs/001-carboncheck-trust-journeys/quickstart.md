# Quickstart - CarbonCheck Trust Journeys

## Goal
Validate end-to-end behavior for single verify, bulk verify, leaderboard, health, and forced fallback mode without returning HTTP 500.

## End-to-End Data Flow
1. User/client submits credit ID input to POST /api/verify.
2. API validates payload shape:
   - single mode: credit_id present
   - bulk mode: credit_ids array length 1..50
3. API normalizes IDs and assigns request_id.
4. For each required external source (Ember, CEA, Grid-India, REC Registry):
   - call with strict 3-second timeout
   - on timeout/error, fetch latest cache rows from Supabase
5. API assembles source snapshot and computes per-check values:
   - baseline_match
   - additionality
   - permanence_risk
   - double_counting
6. API computes weighted trust_score, verdict, evidence summary, and data_mode (live/mixed/cache).
7. API upserts latest score result into trust_scores and returns response envelope.
8. Scheduler refreshes leaderboard_cache every 60 seconds from recent trust_scores.
9. GET /api/leaderboard serves precomputed rankings from leaderboard_cache.
10. GET /api/health returns upstream health + cache readiness, always 200 or 503 (never 500).

## Fallback Contract
- Every external API call timeout: 3 seconds hard limit.
- Fallback precedence: live source -> Supabase cache -> UNSCORED domain response.
- HTTP 500 is disallowed. Unhandled exceptions must map to structured 503/422/429 responses.

## Verify Endpoint Examples

### Single ID
```bash
curl -s -X POST "$API_BASE/api/verify" \
  -H 'Content-Type: application/json' \
  -d '{"credit_id":"REC-IN-2024-001"}'
```

Expected:
- HTTP 200
- one result item with four-check breakdown
- verdict + trust_score + fallback_used flag

### Bulk (50 IDs max)
```bash
curl -s -X POST "$API_BASE/api/verify" \
  -H 'Content-Type: application/json' \
  -d '{"credit_ids":["REC-IN-2024-001","REC-IN-2024-002"]}'
```

Expected:
- HTTP 200
- ranked results by risk severity
- per-item error for invalid IDs, without failing valid IDs

## Leaderboard
```bash
curl -s "$API_BASE/api/leaderboard?credit_type=Forestry&limit=10"
```

Expected:
- HTTP 200
- ranked entries with category, flagged_count_24h, freshness_state

## Health
```bash
curl -s "$API_BASE/api/health"
```

Expected:
- HTTP 200 (healthy/degraded) or 503 (critical dependency unavailable)
- machine-readable upstream and cache status

## Demo Smoke Checklist
- Known risky single ID returns FAIL in <5s.
- Bulk request returns ranked output with stable ordering.
- Leaderboard visible with no auth.
- Forced upstream timeout still returns non-500 response using cache fallback.

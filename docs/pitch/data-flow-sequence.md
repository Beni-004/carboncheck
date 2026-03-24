# Data Flow Sequence: Input to Trust Score

**Task ID**: T019 (Foundational Phase)  
**Purpose**: Visual walkthrough of request-to-response flow with timeout + fallback behavior  
**Audience**: Technical judges who ask "How does the scoring actually work?"

---

## Overview

This document traces one credit ID from API request through external source calls, scoring computation, cache persistence, and final response envelope—including the fallback path when upstream sources fail.

---

## Happy Path: All Sources Respond

```
┌─────────────┐
│   Browser   │
│             │
└──────┬──────┘
       │
       │ POST /api/verify
       │ {"credit_id": "FOR-2891-IND-2019"}
       ↓
┌─────────────────────────────────────────────┐
│         FastAPI: POST /api/verify           │
│  1. Pydantic validates request schema       │
│  2. Generate request_id (UUID)              │
│  3. Parse credit_id format                  │
└──────┬──────────────────────────────────────┘
       │
       │ Pass to verify_service.py
       ↓
┌─────────────────────────────────────────────┐
│      verify_service.verify_single()         │
│  4. Create 4 parallel async tasks:          │
│     • fetch_ember(credit_id)                │
│     • fetch_cea(credit_id)                  │
│     • fetch_grid_india(credit_id)           │
│     • fetch_rec_registry(credit_id)         │
│  5. asyncio.gather() with 3s timeout each   │
└──────┬──────────────────────────────────────┘
       │
       ├──→ Ember API (responds in 1.2s)
       ├──→ CEA Registry (responds in 0.8s)
       ├──→ Grid-India (responds in 2.1s)
       └──→ REC Registry (responds in 1.5s)
       │
       │ All 4 sources return SourceData
       ↓
┌─────────────────────────────────────────────┐
│       scoring/engine.compute_score()        │
│  6. Extract fraud signals from 4 sources    │
│  7. Run 4-check scoring:                    │
│     • baseline_match: 12/100 (weight 0.30)  │
│     • additionality: 45/100 (weight 0.25)   │
│     • permanence_risk: 8/100 (weight 0.25)  │
│     • double_counting: 78/100 (weight 0.20) │
│  8. Weighted average:                       │
│     (12×0.30 + 45×0.25 + 8×0.25 + 78×0.20)  │
│     = 3.6 + 11.25 + 2.0 + 15.6 = 32.45      │
│  9. Round to integer: 32                    │
│  10. Map to verdict:                        │
│      0-39 → FAIL                            │
│      40-69 → WARNING                        │
│      70-100 → PASS                          │
│      Score 32 → FAIL                        │
└──────┬──────────────────────────────────────┘
       │
       │ Return VerifyResult object
       ↓
┌─────────────────────────────────────────────┐
│   trust_score_repository.persist()          │
│  11. Insert into trust_scores table:        │
│      • credit_id                            │
│      • trust_score: 32                      │
│      • verdict: FAIL                        │
│      • checks (JSON)                        │
│      • provenance (JSON)                    │
│      • created_at (timestamp)               │
└──────┬──────────────────────────────────────┘
       │
       │ DB write succeeds
       ↓
┌─────────────────────────────────────────────┐
│       FastAPI: Response Envelope            │
│  12. Build VerifyResponse:                  │
│      {                                      │
│        "request_id": "550e8400-...",        │
│        "mode": "single",                    │
│        "data_mode": "live",                 │
│        "fallback_used": false,              │
│        "timeout_seconds": 3,                │
│        "results": [{ ... }],                │
│        "errors": []                         │
│      }                                      │
│  13. Return HTTP 200                        │
└──────┬──────────────────────────────────────┘
       │
       │ JSON response
       ↓
┌─────────────┐
│   Browser   │
│  (displays  │
│   FAIL UI)  │
└─────────────┘
```

**Total latency**: ~2.5 seconds (longest source call + scoring overhead)

---

## Failure Path: One Source Times Out

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ POST /api/verify
       ↓
┌─────────────────────────────────────────────┐
│      verify_service.verify_single()         │
│  1-5. Same as happy path                    │
└──────┬──────────────────────────────────────┘
       │
       ├──→ Ember API (responds in 1.2s) ✓
       ├──→ CEA Registry (timeout after 3.0s) ✗
       ├──→ Grid-India (responds in 2.1s) ✓
       └──→ REC Registry (responds in 1.5s) ✓
       │
       │ 3 live sources + 1 timeout
       ↓
┌─────────────────────────────────────────────┐
│   clients/cea_client.fallback_from_cache()  │
│  6. Query trust_scores table:               │
│     WHERE credit_id = 'FOR-2891-IND-2019'   │
│       AND source = 'cea'                    │
│     ORDER BY created_at DESC                │
│     LIMIT 1                                 │
│  7. Found cached entry from 2 hours ago     │
│  8. Return SourceData(                      │
│       source='cea',                         │
│       fetched_at='2026-03-24T12:30:00Z',    │
│       freshness_state='stale',              │
│       from_cache=True,                      │
│       data={...cached payload}              │
│     )                                       │
└──────┬──────────────────────────────────────┘
       │
       │ Now have 4 SourceData objects (3 fresh, 1 stale)
       ↓
┌─────────────────────────────────────────────┐
│       scoring/engine.compute_score()        │
│  9. Same scoring logic as happy path        │
│  10. Trust score still computes to 32       │
│  11. Verdict still FAIL                     │
│      (Cached CEA data shows same baseline   │
│       documentation gap as before)          │
└──────┬──────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────┐
│       FastAPI: Response Envelope            │
│  12. Build VerifyResponse with mixed mode:  │
│      {                                      │
│        "data_mode": "mixed",  ← changed     │
│        "fallback_used": true, ← changed     │
│        "results": [{                        │
│          "provenance": [                    │
│            {"source": "ember_api",          │
│             "freshness_state": "fresh",     │
│             "from_cache": false},           │
│            {"source": "cea",                │
│             "freshness_state": "stale", ←   │
│             "from_cache": true},        ←   │
│            {"source": "grid_india",         │
│             "freshness_state": "fresh",     │
│             "from_cache": false},           │
│            {"source": "rec_registry",       │
│             "freshness_state": "fresh",     │
│             "from_cache": false}            │
│          ]                                  │
│        }],                                  │
│        "errors": []                         │
│      }                                      │
│  13. Return HTTP 200 (still success)        │
└──────┬──────────────────────────────────────┘
       │
       ↓
┌─────────────┐
│   Browser   │
│  (displays  │
│   FAIL UI   │
│   + stale   │
│   badge)    │
└─────────────┘
```

**Total latency**: ~3.1 seconds (CEA timeout + scoring overhead)  
**User impact**: Still gets score, sees "1 source used cached data" badge

---

## Catastrophic Failure Path: All Sources Timeout + No Cache

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ POST /api/verify
       ↓
┌─────────────────────────────────────────────┐
│      verify_service.verify_single()         │
└──────┬──────────────────────────────────────┘
       │
       ├──→ Ember API (timeout after 3.0s) ✗
       ├──→ CEA Registry (timeout after 3.0s) ✗
       ├──→ Grid-India (timeout after 3.0s) ✗
       └──→ REC Registry (timeout after 3.0s) ✗
       │
       │ All 4 sources timeout
       ↓
┌─────────────────────────────────────────────┐
│   clients/*/fallback_from_cache()           │
│  • Query trust_scores for each source       │
│  • No cached entries found (new credit ID)  │
│  • Return SourceData(freshness_state =      │
│           'missing', from_cache=True)       │
└──────┬──────────────────────────────────────┘
       │
       │ 4 SourceData objects, all missing
       ↓
┌─────────────────────────────────────────────┐
│       scoring/engine.compute_score()        │
│  • Cannot compute score without data        │
│  • Raise UnscoredError("No source data")    │
└──────┬──────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────┐
│    middleware/error_mapper.py               │
│  • Catch UnscoredError                      │
│  • Map to domain error code:                │
│    UNSCORED_NO_DATA                         │
└──────┬──────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────┐
│       FastAPI: Error Envelope               │
│  {                                          │
│    "request_id": "...",                     │
│    "mode": "single",                        │
│    "data_mode": "cache",                    │
│    "fallback_used": true,                   │
│    "results": [],                           │
│    "errors": [{                             │
│      "credit_id": "FOR-2891-IND-2019",      │
│      "code": "UNSCORED_NO_DATA",            │
│      "message": "No live or cached data     │
│                  available; sources         │
│                  unreachable."              │
│    }]                                       │
│  }                                          │
│  HTTP 200 (not 500)                         │
└──────┬──────────────────────────────────────┘
       │
       ↓
┌─────────────┐
│   Browser   │
│  (displays  │
│   error UI  │
│   with      │
│   retry     │
│   button)   │
└─────────────┘
```

**Total latency**: ~12 seconds (4 sources × 3s timeout)  
**User impact**: Clear error message, encouraged to retry  
**System behavior**: No HTTP 500, error tracked in logs for ops team

---

## Bulk Verification Flow (50 IDs)

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ POST /api/verify
       │ {"credit_ids": ["FOR-2891-...", "REN-4402-...", ...]} (50 IDs)
       ↓
┌─────────────────────────────────────────────┐
│      verify_service.verify_bulk()           │
│  1. Validate payload: 1 ≤ len ≤ 50          │
│  2. Create 50 verify_single() tasks         │
│  3. asyncio.gather(*tasks)                  │
│     • Each task follows single-ID flow      │
│     • All 50 run in parallel                │
│     • Individual timeouts enforced per ID   │
└──────┬──────────────────────────────────────┘
       │
       │ 50 parallel execution paths
       │ (each follows diagram above)
       ↓
┌─────────────────────────────────────────────┐
│       scoring/ranker.rank_by_risk()         │
│  4. Separate successes from errors          │
│  5. Sort successes by trust_score ascending │
│     (lowest score = highest risk = rank 1)  │
│  6. Assign rank field to each result        │
└──────┬──────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────┐
│       FastAPI: Bulk Response Envelope       │
│  {                                          │
│    "request_id": "...",                     │
│    "mode": "bulk",                          │
│    "data_mode": "mixed",                    │
│    "fallback_used": true,                   │
│    "results": [                             │
│      { "credit_id": "REN-4402-CHN-2021",    │
│        "trust_score": 18,                   │
│        "verdict": "FAIL",                   │
│        "rank": 1 },  ← highest risk         │
│      { "credit_id": "FOR-2891-IND-2019",    │
│        "trust_score": 23,                   │
│        "verdict": "FAIL",                   │
│        "rank": 2 },                         │
│      ... (48 more, sorted by score)         │
│    ],                                       │
│    "errors": [                              │
│      { "credit_id": "INVALID-ID",           │
│        "code": "INVALID_ID",                │
│        "message": "Credit ID format..." }   │
│    ]                                        │
│  }                                          │
│  HTTP 200                                   │
└──────┬──────────────────────────────────────┘
       │
       ↓
┌─────────────┐
│   Browser   │
│  (displays  │
│   ranked    │
│   fraud     │
│   table)    │
└─────────────┘
```

**Total latency**: ~5-8 seconds (depends on slowest source across all 50 IDs)  
**Parallelism**: 50 IDs × 4 sources = 200 potential API calls, but only ~20 concurrent (rate-limited)

---

## Leaderboard Refresh Flow

```
┌─────────────────────────────────────────────┐
│   Scheduled Job (every 5 minutes)           │
│   • Cron or Railway background worker       │
└──────┬──────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────┐
│  leaderboard_refresh_service.refresh()      │
│  1. Query trust_scores table:               │
│     SELECT credit_id,                       │
│            credit_type,                     │
│            COUNT(*) as flagged_count,       │
│            AVG(trust_score) as avg_score,   │
│            MAX(created_at) as last_flagged  │
│     FROM trust_scores                       │
│     WHERE created_at > NOW() - INTERVAL     │
│           '30 days'                         │
│       AND verdict IN ('FAIL', 'WARNING')    │
│     GROUP BY credit_id, credit_type         │
│     ORDER BY flagged_count DESC,            │
│              avg_score ASC                  │
│     LIMIT 100                               │
└──────┬──────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────┐
│  2. Compute global and per-type ranks       │
│     • Rank 1 = most flagged globally        │
│     • Rank 1 per type = most flagged in     │
│       Forestry/Renewable/Soil               │
└──────┬──────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────┐
│  3. Truncate and reload leaderboard_cache   │
│     • DELETE FROM leaderboard_cache         │
│     • INSERT new ranked entries             │
│     • Set snapshot_at = NOW()               │
└──────┬──────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────┐
│  4. Mark freshness state                    │
│     • snapshot_at < 5 min ago → fresh       │
│     • snapshot_at < 15 min ago → stale      │
│     • snapshot_at > 15 min ago → degraded   │
└─────────────────────────────────────────────┘

Later...

┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ GET /api/leaderboard?credit_type=Forestry
       ↓
┌─────────────────────────────────────────────┐
│  leaderboard_router.get_leaderboard()       │
│  1. SELECT * FROM leaderboard_cache         │
│     WHERE credit_type = 'Forestry'          │
│        OR credit_type IS NULL (for global)  │
│     ORDER BY rank_by_type ASC               │
│     LIMIT 25                                │
│  2. Check snapshot_at age                   │
│  3. Return LeaderboardResponse with         │
│     freshness_state                         │
└──────┬──────────────────────────────────────┘
       │
       ↓
┌─────────────┐
│   Browser   │
│  (displays  │
│   ranked    │
│   credits)  │
└─────────────┘
```

**Leaderboard latency**: <500ms (cached table read, no external calls)  
**Refresh cost**: ~2-3 seconds every 5 minutes (background job)

---

## Key Latency Breakdown

| Operation | Latency | Bottleneck |
|-----------|---------|------------|
| **Single verify (happy path)** | 2-3s | Slowest of 4 parallel source calls |
| **Single verify (1 timeout)** | 3-4s | 3s timeout + cache lookup |
| **Single verify (all timeout, cached)** | 3-4s | 3s timeout + 4 cache lookups |
| **Single verify (all timeout, no cache)** | 12s | 4 × 3s sequential timeouts |
| **Bulk verify (50 IDs, happy)** | 5-8s | Slowest source across 50 IDs |
| **Bulk verify (50 IDs, mixed)** | 8-12s | Some timeouts + fallback overhead |
| **Leaderboard read** | <500ms | Postgres SELECT from cache table |
| **Leaderboard refresh** | 2-3s | Aggregation query over 30 days |

---

## Demo Talking Points

### For Technical Judges

**When showing single verify:**
> "Notice the provenance array—each source shows whether it came from live API or cache, with a timestamp. This is deterministic: same source snapshot hash = same score every time."

**When asked about parallelism:**
> "We use `asyncio.gather()` to run all four source calls in parallel. Each has a hard 3-second timeout. If one times out, the other three still complete. Total latency is bounded by the slowest source, not the sum of all four."

**When asked about failure handling:**
> "If all sources time out and there's no cache, we return HTTP 200 with an error envelope. The user sees 'UNSCORED_NO_DATA' instead of a cryptic 500. The frontend shows a retry button. This is a domain error, not a system crash."

### For Business Judges

**When showing bulk API:**
> "A traditional audit would take 50 credits × 5 minutes per credit = 4 hours of manual work. With our bulk API, the auditor gets a ranked fraud report in 18 seconds. The top three riskiest credits are surfaced immediately—that's where they spend their investigation time."

**When showing leaderboard:**
> "This leaderboard refreshes every 5 minutes. It's fast because we pre-compute rankings in the background. The public page loads in under a second, no login required. Journalists can cite these numbers in articles, and buyers can bookmark this page for due diligence."

---

## Error Scenarios Summary

| Scenario | HTTP Code | Response Envelope | User Experience |
|----------|-----------|-------------------|-----------------|
| **All sources succeed** | 200 | `data_mode: "live"`, `fallback_used: false` | Green badges, "all sources fresh" |
| **1 source timeout, cache hit** | 200 | `data_mode: "mixed"`, `fallback_used: true` | Yellow badge, "1 source stale" |
| **All timeout, cache hit** | 200 | `data_mode: "cache"`, `fallback_used: true` | Yellow badges, "all sources stale" |
| **All timeout, no cache** | 200 | `errors: [UNSCORED_NO_DATA]` | Error panel, "retry in 1 minute" |
| **Invalid ID format** | 422 | `errors: [INVALID_ID]` | Validation error, show format example |
| **Rate limit hit** | 429 | `code: "RATE_LIMIT_EXCEEDED"` | Retry-After header, upgrade prompt |
| **Supabase down** | 503 | `status: "degraded"`, `code: "CACHE_UNAVAILABLE"` | Degraded badge, "service degraded" |
| **Unknown exception** | 503 | `status: "degraded"`, `code: "UNKNOWN_ERROR"` | Generic error, ops team alerted |

**Never returns HTTP 500.**

---

## Success Metrics

- **Judge asks "Can you show me the timeout in action?"** → Demo backup scenario where we simulate CEA timeout.
- **Judge says "So you never return 500?"** → Confirm: "Correct, all errors are domain errors with structured envelopes."
- **Judge asks "How do you make it deterministic?"** → Show source snapshot hash generation in code.
- **Judge nods at parallel execution diagram** → They understand the async architecture.

---

## Diagram Legend

```
┌─────────────┐
│   System    │  ← Box represents a system component
└──────┬──────┘
       │          ← Arrow shows data flow direction
       ↓
┌─────────────┐
│   Process   │
│  1. Step A  │  ← Numbered steps inside box
│  2. Step B  │
└─────────────┘

✓ Success
✗ Failure/Timeout
← Arrow with note
```

---

## Rehearsal Notes

- Practice narrating the happy path in 30 seconds (judges have short attention spans).
- If a judge asks about failure handling, walk through the timeout scenario line-by-line.
- If a judge asks "What happens if...?", find the matching scenario in this doc and use it verbatim.
- Keep this doc open on laptop during demo for quick reference.

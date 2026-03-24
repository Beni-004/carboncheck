# Phase 0 Research - CarbonCheck Trust Journeys

## Decision 1: Scoring model shape and thresholds
- Decision: Use a deterministic weighted score from four checks: baseline_match (30), additionality (25), permanence_risk (25), double_counting (20), clamped to 0-100.
- Rationale: Simple enough for hackathon velocity, explainable in demos, and deterministic by design.
- Alternatives considered:
  - ML classifier: rejected due to lower explainability and model drift risk during live demo.
  - Equal weighting: rejected because baseline and permanence signals have higher fraud impact in domain feedback.

## Decision 2: API design for single and bulk verify
- Decision: Use one endpoint POST /api/verify that accepts either one credit_id or up to 50 credit_ids and returns per-item deterministic breakdown plus ranking metadata for batch mode.
- Rationale: One canonical contract reduces client complexity and avoids duplicate scoring paths.
- Alternatives considered:
  - Separate /api/verify and /api/verify-bulk: rejected due to duplicated validation and scoring logic.

## Decision 3: External source integration resilience
- Decision: Each external source call uses a 3-second timeout and independent fallback to Supabase cache; unresolved sources become stale/missing signals but still return a non-500 response.
- Rationale: Meets hard no-500 rule and preserves user outcomes during partial outages.
- Alternatives considered:
  - Global request timeout only: rejected because one slow source could consume full latency budget.
  - Hard fail when any source fails: rejected because it violates constitution reliability and fallback principles.

## Decision 4: Data freshness semantics
- Decision: Every source record stores fetched_at and stale_after timestamps; response includes data_mode = live | mixed | cache and fallback_used boolean.
- Rationale: Provides transparent provenance and supports audit trust.
- Alternatives considered:
  - Omit freshness metadata: rejected because auditors and journalists need source confidence context.

## Decision 5: Leaderboard architecture
- Decision: Maintain leaderboard_cache as a precomputed table refreshed by scheduled job every 60 seconds and read via GET /api/leaderboard.
- Rationale: Guarantees fast public reads and stable demo UX.
- Alternatives considered:
  - Compute on each request: rejected due to latency variability and avoidable load.

## Decision 6: Error contract strategy (never HTTP 500)
- Decision: Return 2xx/4xx only. Operational failures are represented via domain error envelope (status = degraded/error, fallback_used, errors[]).
- Rationale: Delivers predictable client behavior and satisfies explicit requirement to never return 500.
- Alternatives considered:
  - Default framework exception handling: rejected because uncaught errors can produce 500 and break demos.

## Decision 7: Abuse control for public and API surfaces
- Decision: Apply token-bucket limits at gateway and app-level validation limits (single ID or <=50 IDs, bounded payload size).
- Rationale: Protects demo stability and aligns with constitution security guardrails.
- Alternatives considered:
  - App-only throttling: rejected due to weaker edge protection.

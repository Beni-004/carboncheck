# Tasks: CarbonCheck Trust Journeys

**Input**: Design documents from `/specs/001-carboncheck-trust-journeys/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md
**Organization**: Tasks are grouped by user story and constrained by 4-agent execution buckets.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on incomplete tasks)
- **[Story]**: User story label (`[US1]`, `[US2]`, `[US3]`) for story-phase tasks only
- Every task includes an explicit file path

## Agent Buckets (The Hijack)

### [AGENT 1: FRONTEND]
- Allowed paths: `apps/web/**`
- Forbidden paths: `apps/api/**`, `supabase/**`, `specs/001-carboncheck-trust-journeys/contracts/**`
- Scope: UI, client-side state, UX polish, no backend routing logic

### [AGENT 2: BACKEND]
- Allowed paths: `apps/api/**`, `supabase/**`, `specs/001-carboncheck-trust-journeys/contracts/**`
- Forbidden paths: `apps/web/**`, `docs/pitch/**`
- Scope: schema, scoring engine, API routes, fallback, never-500 behavior

### [AGENT 3: INTEGRATOR]
- Start condition: ONLY after Agent 1 and Agent 2 branches are merged to `main`
- Allowed paths: cross-stack wiring files in `apps/web/**`, `apps/api/**`, infra glue in `supabase/**`
- Scope: end-to-end integration, smoke validation, release hardening

### [AGENT 4: PITCH/DOCS]
- Allowed paths: `docs/pitch/**`, `specs/001-carboncheck-trust-journeys/**`
- Forbidden paths: `apps/web/**`, `apps/api/**`, `supabase/**`
- Scope: demo narrative, evidence pack, runbooks, judge-facing artifacts

---

## Phase 1: Setup (Parallel Sprint Kickoff)

**Purpose**: Establish isolated workstreams and baseline structure for the 24-hour sprint.

- [ ] T001 [P] Create frontend app skeleton in apps/web/app/layout.tsx
- [ ] T002 [P] Create backend app skeleton in apps/api/app/main.py
- [ ] T003 [P] Create scoring package skeleton in apps/api/app/scoring/__init__.py
- [ ] T004 [P] Create migration scaffold for rigid schema in supabase/migrations/20260324_001_init_carboncheck.sql
- [ ] T005 [P] Create pitch workspace index in docs/pitch/README.md
- [ ] T006 [P] Create worktree coordination guide in docs/pitch/worktree-boundaries.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core platform and contract guarantees that must be complete before user story implementation.

**CRITICAL**: User story implementation starts only after this phase is complete.

- [ ] T007 Implement carbon_credits, trust_scores, leaderboard_cache DDL in supabase/migrations/20260324_001_init_carboncheck.sql
- [ ] T008 Add deterministic scoring formula constants in apps/api/app/scoring/constants.py
- [ ] T009 Add Pydantic request/response schemas for verify/leaderboard/health in apps/api/app/schemas.py
- [ ] T010 Implement upstream client timeout wrapper (3 seconds fixed) in apps/api/app/clients/base_client.py
- [ ] T011 [P] Implement Ember API client with timeout + cache fallback hooks in apps/api/app/clients/ember_client.py
- [ ] T012 [P] Implement CEA client with timeout + cache fallback hooks in apps/api/app/clients/cea_client.py
- [ ] T013 [P] Implement Grid-India client with timeout + cache fallback hooks in apps/api/app/clients/grid_india_client.py
- [ ] T014 [P] Implement REC Registry client with timeout + cache fallback hooks in apps/api/app/clients/rec_registry_client.py
- [ ] T015 Implement cache repository for source fallback reads/writes in apps/api/app/services/cache_repository.py
- [ ] T016 Implement global exception mapper to disallow HTTP 500 in apps/api/app/middleware/error_mapper.py
- [ ] T017 Wire middleware and router registration in apps/api/app/main.py
- [ ] T018 Align OpenAPI contract examples with timeout/fallback envelope in specs/001-carboncheck-trust-journeys/contracts/openapi.yaml
- [ ] T019 Create architecture sequence diagram for input-to-score flow in docs/pitch/data-flow-sequence.md

**Checkpoint**: Foundation complete; user stories can begin.

---

## Phase 3: User Story 1 - Stop a Bad Purchase Instantly (Priority: P1) MVP

**Goal**: A buyer pastes one credit ID and gets score + FAIL/WARNING/PASS + evidence in under 5 seconds.

**Independent Test**: Submit one known risky ID and verify FAIL response with check breakdown and provenance under 5 seconds.

- [ ] T020 [US1] Implement four-check scoring engine (baseline_match, additionality, permanence_risk, double_counting) in apps/api/app/scoring/engine.py
- [ ] T021 [US1] Implement single-item verify service orchestration in apps/api/app/services/verify_service.py
- [ ] T022 [US1] Implement POST /api/verify single-ID path in apps/api/app/routers/verify.py
- [ ] T023 [US1] Persist single verification result to trust_scores in apps/api/app/services/trust_score_repository.py
- [ ] T024 [US1] Add deterministic source snapshot hash generation in apps/api/app/scoring/snapshot_hash.py
- [ ] T025 [US1] Add fallback_used and data_mode propagation in API response schema at apps/api/app/schemas.py
- [ ] T026 [US1] Add backend unit coverage for deterministic scoring in apps/api/tests/test_scoring_determinism.py
- [ ] T027 [US1] Add backend outage simulation coverage for fallback path in apps/api/tests/test_verify_fallback.py
- [ ] T028 [P] [US1] Build single-ID verify form UI in apps/web/app/verify/page.tsx
- [ ] T029 [P] [US1] Implement verify API client adapter in apps/web/lib/api/verifyClient.ts
- [ ] T030 [US1] Implement Trust Score result card with 4-check breakdown in apps/web/components/TrustScoreCard.tsx
- [ ] T031 [US1] Add FAIL/WARNING/PASS visual treatment and evidence panel in apps/web/components/ScoreVerdictBanner.tsx
- [ ] T032 [US1] Add fallback mode and freshness badges in apps/web/components/ProvenanceBadges.tsx
- [ ] T033 [US1] Capture MVP demo script for buyer journey in docs/pitch/us1-demo-script.md

**Checkpoint**: User Story 1 is independently functional and demo-ready.

---

## Phase 4: User Story 2 - Audit 50 Credits in One Call (Priority: P2)

**Goal**: Auditor submits up to 50 IDs and receives ranked fraud report with per-ID error handling.

**Independent Test**: Submit a mixed-validity list of 50 IDs and verify ranked results with no loss of valid entries.

- [ ] T034 [US2] Extend verify service for bulk mode (1..50 IDs) in apps/api/app/services/verify_service.py
- [ ] T035 [US2] Implement ranking logic for risk ordering in apps/api/app/scoring/ranker.py
- [ ] T036 [US2] Add per-item validation/error envelope handling in apps/api/app/routers/verify.py
- [ ] T037 [US2] Persist rank_in_batch for bulk evaluations in apps/api/app/services/trust_score_repository.py
- [ ] T038 [US2] Add backend coverage for 50-ID bulk happy path in apps/api/tests/test_verify_bulk_success.py
- [ ] T039 [US2] Add backend coverage for mixed valid/invalid bulk inputs in apps/api/tests/test_verify_bulk_partial_errors.py
- [ ] T040 [P] [US2] Build bulk upload input and list preview UI in apps/web/app/verify/bulk/page.tsx
- [ ] T041 [P] [US2] Implement ranked fraud table component in apps/web/components/BulkFraudReportTable.tsx
- [ ] T042 [US2] Add CSV export action for ranked results in apps/web/components/BulkExportButton.tsx
- [ ] T043 [US2] Create auditor talk-track and ROI proof points in docs/pitch/us2-auditor-value.md

**Checkpoint**: User Story 2 independently works with ranked bulk output and partial-error behavior.

---

## Phase 5: User Story 3 - Public Leaderboard of Shame (Priority: P3)

**Goal**: No-login leaderboard shows most-flagged credits by Forestry/Renewable/Soil in near real time.

**Independent Test**: Open leaderboard in anonymous browser and verify category-ranked entries with freshness state.

- [ ] T044 [US3] Implement leaderboard refresh job from trust_scores into leaderboard_cache in apps/api/app/services/leaderboard_refresh_service.py
- [ ] T045 [US3] Implement GET /api/leaderboard route with filters in apps/api/app/routers/leaderboard.py
- [ ] T046 [US3] Implement GET /api/health dependency status route in apps/api/app/routers/health.py
- [ ] T047 [US3] Add backend coverage for leaderboard filter + limit behavior in apps/api/tests/test_leaderboard_api.py
- [ ] T048 [US3] Add backend coverage for health degraded/unavailable states in apps/api/tests/test_health_api.py
- [ ] T049 [P] [US3] Build public leaderboard page in apps/web/app/leaderboard/page.tsx
- [ ] T050 [P] [US3] Implement leaderboard category tabs and rank cards in apps/web/components/LeaderboardTabs.tsx
- [ ] T051 [US3] Add no-login public navigation entry to leaderboard in apps/web/components/NavBar.tsx
- [ ] T052 [US3] Create journalist storyline and screenshots checklist in docs/pitch/us3-journalist-story.md

**Checkpoint**: User Story 3 is independently functional and public-facing.

---

## Phase 6: Agent 3 Integration (Post-Merge Only)

**Purpose**: Integrate frontend + backend branches only after Agent 1 and Agent 2 merge to `main`.

- [ ] T053 Merge Agent 1 frontend branch into main and resolve conflicts in apps/web/app/verify/page.tsx
- [ ] T054 Merge Agent 2 backend branch into main and resolve conflicts in apps/api/app/routers/verify.py
- [ ] T055 Wire frontend verify and leaderboard calls to merged backend endpoints in apps/web/lib/api/verifyClient.ts
- [ ] T056 Validate end-to-end single verify flow against merged API in apps/web/app/verify/page.tsx
- [ ] T057 Validate end-to-end bulk verify flow against merged API in apps/web/app/verify/bulk/page.tsx
- [ ] T058 Validate public leaderboard and health integration against merged API in apps/web/app/leaderboard/page.tsx
- [ ] T059 Execute forced upstream-timeout smoke run and verify non-500 responses in specs/001-carboncheck-trust-journeys/quickstart.md

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, demo readiness, and judge-facing delivery assets.

- [ ] T060 [P] Optimize backend response latency hotspots for p95 target in apps/api/app/services/verify_service.py
- [ ] T061 [P] Optimize frontend first-render and loading states in apps/web/app/verify/page.tsx
- [ ] T062 [P] Create final demo runbook with minute-by-minute sequence in docs/pitch/final-demo-runbook.md
- [ ] T063 [P] Prepare architecture one-pager for judges in docs/pitch/architecture-one-pager.md
- [ ] T064 Final quickstart validation and evidence capture in specs/001-carboncheck-trust-journeys/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Starts immediately; Agent 1, Agent 2, Agent 4 run in parallel.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phase 3-5 (User Stories)**: Depend on Phase 2 completion; Agent 1/2/4 continue in parallel within allowed path boundaries.
- **Phase 6 (Agent 3 Integration)**: MUST start only after Agent 1 and Agent 2 branches are merged to `main`.
- **Phase 7 (Polish)**: Depends on Phase 6 integration validation.

### User Story Dependencies

- **US1 (P1)**: No dependency on US2/US3 once foundational work is complete.
- **US2 (P2)**: Reuses verify foundation from US1 but remains independently testable.
- **US3 (P3)**: Depends on score persistence and refresh pipeline, remains independently testable as public view.

### Agent Dependency Rules

- Agent 1, Agent 2, and Agent 4 run concurrently in isolated worktrees.
- Agent 1, Agent 2, and Agent 4 MUST NOT modify each other's file scopes.
- Agent 3 starts only after frontend and backend branches are merged to main.
- Any cross-boundary change request must be queued for Agent 3 integration phase.

---

## Parallel Execution Examples

### User Story 1 Parallel Launch

```bash
# Agent 2 (backend) in parallel:
T020, T021, T022, T023, T024, T025

# Agent 1 (frontend) in parallel:
T028, T029, T030, T031, T032

# Agent 4 (pitch/docs) in parallel:
T033
```

### User Story 2 Parallel Launch

```bash
# Agent 2 (backend) in parallel:
T034, T035, T036, T037

# Agent 1 (frontend) in parallel:
T040, T041, T042

# Agent 4 (pitch/docs) in parallel:
T043
```

### User Story 3 Parallel Launch

```bash
# Agent 2 (backend) in parallel:
T044, T045, T046

# Agent 1 (frontend) in parallel:
T049, T050, T051

# Agent 4 (pitch/docs) in parallel:
T052
```

---

## Implementation Strategy

### MVP First (US1 in 24-Hour Sprint)

1. Complete Phases 1 and 2 before hour 6.
2. Complete US1 implementation and validation by hour 12.
3. Freeze US1 demo path and avoid scope creep.

### Incremental Delivery

1. Deliver US1 for core anti-fraud value.
2. Add US2 for enterprise audit upside.
3. Add US3 for public wow-factor and storytelling.
4. Run Agent 3 integration only after branch merges.

### Hackathon Manager Playbook

1. Every 2 hours, run dependency check against phase gates.
2. Block cross-agent file edits outside assigned bucket.
3. Keep one demo-safe branch tagged after each story checkpoint.

# Tasks: CarbonCheck Trust Journeys

**Input**: Design documents from `/specs/001-carboncheck-trust-journeys/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md
**Organization**: Tasks are grouped by user story and constrained by 4-agent execution buckets.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on incomplete tasks)
- **[Story]**: User story label (`[US1]`, `[US2]`, `[US3]`) for story-phase tasks only
- Every task includes an explicit file path

## Agent Buckets (Engineering Manager Assignment)

### [AGENT 1: FRONTEND]
- Allowed paths: `apps/web/**`
- Forbidden paths: `backend/**`, `docs/pitch/**`, `specs/001-carboncheck-trust-journeys/contracts/**`
- Scope: UI surfaces, client-side API adapters, UX states

### [AGENT 2: BACKEND]
- Allowed paths: `backend/**`, `specs/001-carboncheck-trust-journeys/contracts/**`
- Forbidden paths: `apps/web/**`, `docs/pitch/**`
- Scope: API routes, verification engine, data integrations, fallback, non-500 behavior

### [AGENT 3: INTEGRATOR]
- Start condition: ONLY after Agent 1 and Agent 2 branches are merged to `main`
- Allowed paths: `apps/web/**`, `backend/**`, `specs/001-carboncheck-trust-journeys/quickstart.md`
- Scope: end-to-end wiring, smoke validation, release hardening

### [AGENT 4: PITCH/DOCS]
- Allowed paths: `docs/pitch/**`, `specs/001-carboncheck-trust-journeys/**`
- Forbidden paths: `apps/web/**`, `backend/**`
- Scope: demo narrative, evidence pack, runbooks, judge-facing artifacts

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Align current monorepo paths and kickoff workstream ownership.

- [ ] T001 [P] Validate backend app entrypoint and router includes in backend/app/main.py
- [ ] T002 [P] Validate frontend route skeleton for verify and leaderboard in apps/web/app/layout.tsx
- [ ] T003 [P] Refresh worktree boundaries for 4-agent split in docs/pitch/worktree-boundaries.md
- [ ] T004 [P] Confirm API base URL wiring contract in apps/web/lib/api.ts
- [ ] T005 [P] Align quickstart commands with backend runtime script in specs/001-carboncheck-trust-journeys/quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core backend platform and contract guarantees that block all user stories.

**CRITICAL**: User story implementation starts only after this phase is complete.

### Mandatory AGENT 2: BACKEND Starter-Kit Pushdown

- [ ] T006 Append implementation starter-kit dependencies in backend/requirements.txt
- [ ] T007 [P] Scaffold verification engine package root in backend/app/verification_engine/__init__.py
- [ ] T008 [P] Scaffold ground layer package in backend/app/verification_engine/ground_layer/__init__.py
- [ ] T009 [P] Scaffold satellite layer package in backend/app/verification_engine/satellite_layer/__init__.py
- [ ] T010 [P] Scaffold AI layer package in backend/app/verification_engine/ai_layer/__init__.py
- [ ] T011 [P] Scaffold scoring layer package in backend/app/verification_engine/scoring_layer/__init__.py
- [ ] T012 Implement registry client for ground-layer project retrieval in backend/app/verification_engine/ground_layer/registry_client.py
- [ ] T013 Implement Google Earth Engine client for satellite-layer signals in backend/app/verification_engine/satellite_layer/gee_client.py
- [ ] T014 Implement verification engine orchestration facade for verify flows in backend/app/verification_engine/scoring_layer/engine.py
- [ ] T015 Route existing verify service through verification engine facade in backend/app/services/verify_service.py
- [ ] T016 Route existing verify API endpoint through updated service path in backend/app/routers/verify.py

### Shared Foundation

- [ ] T017 Implement deterministic scoring constants and verdict thresholds in backend/app/scoring/constants.py
- [ ] T018 Add verify/leaderboard/health schema models with provenance fields in backend/app/schemas.py
- [ ] T019 Implement 3-second timeout wrapper for upstream calls in backend/app/clients/base_client.py
- [ ] T020 Implement cache repository for fallback reads and writes in backend/app/services/cache_repository.py
- [ ] T021 Implement non-500 exception mapping middleware in backend/app/middleware/error_mapper.py
- [ ] T022 Align OpenAPI verify examples with engine-backed response envelope in specs/001-carboncheck-trust-journeys/contracts/openapi.yaml

**Checkpoint**: Foundation complete; user stories can begin.

---

## Phase 3: User Story 1 - Stop a Bad Purchase Instantly (Priority: P1) 🎯 MVP

**Goal**: A buyer submits one credit ID and receives Trust Score + FAIL/WARNING/PASS + evidence in under 5 seconds.

**Independent Test**: Submit one known risky ID and verify FAIL response with evidence and provenance in under 5 seconds.

- [ ] T023 [US1] Implement single-ID verify orchestration and source snapshot hash in backend/app/services/verify_service.py
- [ ] T024 [US1] Persist single verification output to trust_scores in backend/app/services/trust_score_repository.py
- [ ] T025 [US1] Implement single-ID request/response handling in backend/app/routers/verify.py
- [ ] T026 [US1] Expose fallback_used and data_mode in API schema payload in backend/app/schemas.py
- [ ] T027 [P] [US1] Build single-ID verification form and submit flow in apps/web/app/verify/page.tsx
- [ ] T028 [P] [US1] Implement frontend verify API adapter for single responses in apps/web/lib/api.ts
- [ ] T029 [US1] Render trust score card with 4-check evidence block in apps/web/components/trust-score-card.tsx
- [ ] T030 [US1] Render verdict and provenance badges for single verify result in apps/web/components/provenance-badges.tsx
- [ ] T031 [US1] Capture buyer journey script and acceptance checkpoints in docs/pitch/us1-demo-script.md

**Checkpoint**: User Story 1 is independently functional and demo-ready.

---

## Phase 4: User Story 2 - Audit 50 Credits in One Call (Priority: P2)

**Goal**: Auditor submits up to 50 IDs and receives ranked fraud report with per-ID error handling.

**Independent Test**: Submit 50 IDs (mixed validity) and verify ranked valid results plus explicit invalid-ID errors.

- [ ] T032 [US2] Extend verify orchestration for bulk mode (1..50 IDs) in backend/app/services/verify_service.py
- [ ] T033 [US2] Implement risk ranking utility for bulk ordering in backend/app/scoring/ranker.py
- [ ] T034 [US2] Implement per-ID validation and partial-error envelope in backend/app/routers/verify.py
- [ ] T035 [US2] Persist rank_in_batch for bulk verification rows in backend/app/services/trust_score_repository.py
- [ ] T036 [P] [US2] Implement bulk upload and parsing interaction in apps/web/app/verify/bulk/page.tsx
- [ ] T037 [P] [US2] Render ranked bulk fraud table with sortable columns in apps/web/components/bulk-fraud-report-table.tsx
- [ ] T038 [US2] Render mixed valid/invalid result messaging in apps/web/components/fraud-risk-list.tsx
- [ ] T039 [US2] Capture auditor value narrative for ranked triage in docs/pitch/us2-auditor-value.md

**Checkpoint**: User Story 2 independently works with ranked output and partial-error behavior.

---

## Phase 5: User Story 3 - Public Leaderboard of Shame (Priority: P3)

**Goal**: Public no-login leaderboard shows most-flagged credits by Forestry/Renewable/Soil.

**Independent Test**: Open leaderboard in anonymous session and verify category-ranked entries with freshness metadata.

- [ ] T040 [US3] Implement leaderboard refresh service from trust_scores to cache view in backend/app/services/leaderboard_refresh_service.py
- [ ] T041 [US3] Implement GET /api/leaderboard query handling in backend/app/routers/leaderboard.py
- [ ] T042 [US3] Implement GET /api/health with dependency and cache states in backend/app/routers/health.py
- [ ] T043 [P] [US3] Build public leaderboard page and fetch lifecycle in apps/web/app/leaderboard/page.tsx
- [ ] T044 [P] [US3] Render leaderboard table with category grouping and rank semantics in apps/web/components/leaderboard-table.tsx
- [ ] T045 [US3] Add global navigation link to public leaderboard in apps/web/components/nav-bar.tsx
- [ ] T046 [US3] Capture journalist storyline and supporting evidence checklist in docs/pitch/us3-journalist-story.md

**Checkpoint**: User Story 3 is independently functional and public-facing.

---

## Phase 6: Agent 3 Integration (Post-Merge Only)

**Purpose**: Integrate frontend + backend only after Agent 1 and Agent 2 merge to `main`.

- [ ] T047 Merge Agent 1 frontend branch and resolve verify-page integration in apps/web/app/verify/page.tsx
- [ ] T048 Merge Agent 2 backend branch and resolve engine-route integration in backend/app/routers/verify.py
- [ ] T049 Wire frontend API client to merged backend contract in apps/web/lib/api.ts
- [ ] T050 Validate end-to-end single verify flow against merged backend in apps/web/app/verify/page.tsx
- [ ] T051 Validate end-to-end bulk verify flow against merged backend in apps/web/app/verify/bulk/page.tsx
- [ ] T052 Validate leaderboard and health journeys against merged backend in apps/web/app/leaderboard/page.tsx
- [ ] T053 Execute forced-timeout fallback smoke run and capture non-500 evidence in specs/001-carboncheck-trust-journeys/quickstart.md

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Harden demo readiness, performance, and decision-support documentation.

- [ ] T054 [P] Optimize backend verify latency hotspots toward p95 <5s in backend/app/services/verify_service.py
- [ ] T055 [P] Optimize frontend loading and error states for demo stability in apps/web/app/verify/page.tsx
- [ ] T056 [P] Finalize architecture one-pager with verification engine layering in docs/pitch/architecture-one-pager.md
- [ ] T057 [P] Finalize minute-by-minute live demo runbook in docs/pitch/final-demo-runbook.md
- [ ] T058 Run full quickstart validation and record final evidence checklist in specs/001-carboncheck-trust-journeys/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Starts immediately across all agents.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phase 3-5 (User Stories)**: Depend on Phase 2 completion and can run in parallel by staffing.
- **Phase 6 (Integration)**: Starts only after Agent 1 and Agent 2 are merged to main.
- **Phase 7 (Polish)**: Starts after Phase 6 validation.

### User Story Dependencies

- **US1 (P1)**: Independent once foundational tasks complete.
- **US2 (P2)**: Reuses verify pathways but remains independently testable.
- **US3 (P3)**: Depends on score persistence and cache refresh, remains independently testable.

### Agent Dependency Rules

- Agent 1, Agent 2, and Agent 4 run concurrently in isolated worktrees.
- AGENT 2 owns all starter-kit verification engine tasks (T006-T016) and must complete them before US1 execution.
- Agent 3 may not start until Agent 1 and Agent 2 merges are complete.

---

## Parallel Execution Examples

### User Story 1 Parallel Launch

```bash
# Agent 2 backend tasks in parallel where safe:
T023, T024, T025, T026

# Agent 1 frontend tasks in parallel:
T027, T028, T029, T030

# Agent 4 docs in parallel:
T031
```

### User Story 2 Parallel Launch

```bash
# Agent 2 backend tasks in parallel where safe:
T032, T033, T034, T035

# Agent 1 frontend tasks in parallel:
T036, T037, T038

# Agent 4 docs in parallel:
T039
```

### User Story 3 Parallel Launch

```bash
# Agent 2 backend tasks in parallel where safe:
T040, T041, T042

# Agent 1 frontend tasks in parallel:
T043, T044, T045

# Agent 4 docs in parallel:
T046
```

---

## Implementation Strategy

### MVP First (US1)

1. Complete Phase 1 and Phase 2, with AGENT 2 starter-kit tasks (T006-T016) treated as hard gate.
2. Complete Phase 3 (US1) and validate independent acceptance criteria.
3. Freeze MVP demo lane before expanding to US2 and US3.

### Incremental Delivery

1. Deliver US1 for immediate risk prevention value.
2. Add US2 for audit portfolio triage.
3. Add US3 for public transparency narrative.
4. Run Phase 6 integration and Phase 7 polish for demo hardening.

### Engineering Manager Guardrails

1. Enforce bucket boundaries at each pull request.
2. Hold phase-gate check every 2 hours against blockers.
3. Keep one demo-safe rollback tag after each story checkpoint.

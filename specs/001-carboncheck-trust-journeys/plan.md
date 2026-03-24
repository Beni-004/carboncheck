# Implementation Plan: CarbonCheck Trust Journeys

**Branch**: `001-carboncheck-trust-journeys` | **Date**: 2026-03-24 | **Spec**: `/specs/001-carboncheck-trust-journeys/spec.md`
**Input**: Feature specification from `/specs/001-carboncheck-trust-journeys/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Deliver three production-grade MVP flows: single credit verification, bulk verification (up to 50 IDs), and a public no-login leaderboard. The architecture enforces deterministic 4-check scoring, per-source 3-second timeouts, Supabase cache fallback, and strict non-500 API behavior using domain error envelopes.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Frontend TypeScript (Next.js 14), Backend Python 3.11 (FastAPI)  
**Primary Dependencies**: Next.js 14, FastAPI, Pydantic v2, httpx, Supabase Postgres, Supabase client SDK  
**Storage**: Supabase Postgres with rigid tables: carbon_credits, trust_scores, leaderboard_cache  
**Testing**: pytest (API/domain), Playwright (critical web journey), contract validation against OpenAPI  
**Target Platform**: Vercel (web) and Railway (API)
**Project Type**: Web application + API backend  
**Performance Goals**: POST /api/verify p95 < 5s (single ID), no uncaught 500 responses, stable public leaderboard reads  
**Constraints**: Per external source timeout fixed at 3 seconds; fallback to Supabase cache; bulk payload max 50 IDs; never return HTTP 500  
**Scale/Scope**: Hackathon MVP with live-demo reliability prioritized over feature breadth

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Gate Review

- [x] Demo-first reliability: architecture budgets source calls with strict 3-second timeouts and cache fallback.
- [x] Provenance: contracts require source name, fetched_at timestamp, and freshness state per source.
- [x] Deterministic scoring: weighted formula and source snapshot hash defined for repeatability.
- [x] Outage fallback: source failure path routes to Supabase cached records with fallback_used flag.
- [x] Stack discipline: plan remains within Next.js 14 + FastAPI + Supabase + Vercel + Railway.
- [x] Security guardrails: payload validation and rate-limit behavior specified in API contracts.

### Post-Design Re-Check

- [x] Passed after research + data model + contracts + quickstart generation.
- [x] No constitutional violations detected; Complexity Tracking remains empty.

## Project Structure

### Documentation (this feature)

```text
specs/001-carboncheck-trust-journeys/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
apps/
├── web/
│   ├── app/
│   ├── components/
│   └── lib/
└── api/
    ├── app/
    │   ├── routers/
    │   ├── services/
    │   ├── scoring/
    │   └── clients/
    └── tests/

supabase/
├── migrations/
└── seed/
```

**Structure Decision**: Choose the web application structure (`apps/web` + `apps/api`) with Supabase migrations. This split isolates public UI latency concerns from scoring API resilience logic while staying within the constitution-mandated stack.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

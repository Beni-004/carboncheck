# Implementation Plan: CarbonCheck Trust Journeys

**Branch**: `001-carboncheck-trust-journeys` | **Date**: 2026-03-27 | **Spec**: `/home/iyad/Projects/carboncheck/specs/001-carboncheck-trust-journeys/spec.md`
**Input**: Feature specification from `/home/iyad/Projects/carboncheck/specs/001-carboncheck-trust-journeys/spec.md`

## Summary

Replace the current basic backend calculator with a four-layer verification engine that produces deterministic Trust Scores and explainable evidence for single-check, bulk-audit, and public leaderboard journeys. The backend flow is Ground (registry + document truth), Satellite (Earth Engine NDVI signals), AI (carbon estimate + anomaly detection), and Scoring (policy checks + verdict), with strict timeout/fallback paths to Supabase cache to preserve the sub-5-second demo budget.

## Technical Context

**Language/Version**: Frontend TypeScript (Next.js 14), Backend Python 3.12 (FastAPI)  
**Primary Dependencies**: Next.js 14, FastAPI, Supabase Python client, httpx, pydantic, pdfplumber, beautifulsoup4, lxml, earthengine-api, rasterio, geopandas, shapely, torch, torchvision, torchgeo, scikit-learn, xgboost, pyod, pandas, numpy, redis, pillow, pyproj  
**Storage**: Supabase Postgres for canonical records + score snapshots + leaderboard cache; Supabase cache tables for upstream fallback snapshots  
**Testing**: Frontend unit/integration tests (existing web stack), backend pytest + pytest-asyncio with deterministic scoring tests and outage-fallback integration tests  
**Target Platform**: Vercel (web) + Railway (API)  
**Project Type**: Web app with Python API backend and public endpoints  
**Performance Goals**: Single-ID verify p95 under 5 seconds; bulk 50 IDs under 20 seconds p95; leaderboard p95 under 3 seconds  
**Constraints**: No HTTP 500 from business paths; external calls must use bounded timeouts and degrade to Supabase cache; verdicts must remain deterministic for identical normalized input + source snapshot  
**Scale/Scope**: Hackathon MVP with three user journeys and high demo reliability priority over breadth

## Constitution Check (Pre-Research Gate)

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Demo-first reliability: timeout-bounded upstream calls + cache fallback preserve sub-5-second path for single checks.
- [x] Provenance: response contracts include source identity, fetch timestamps, freshness, and fallback markers.
- [x] Deterministic scoring: scoring layer uses fixed check weights and snapshot hash anchor.
- [x] Outage fallback: cache-first degraded path is explicit in response envelope.
- [x] Stack discipline: architecture stays on Next.js + FastAPI + Supabase + Vercel + Railway.
- [x] Security guardrails: ID validation, payload limits, rate limits, and secrets via platform managers are in scope.

## Project Structure

### Documentation (this feature)

```text
/home/iyad/Projects/carboncheck/specs/001-carboncheck-trust-journeys/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
└── tasks.md
```

### Source Code (repository root)

```text
/home/iyad/Projects/carboncheck/
├── apps/
│   └── web/
│       ├── app/
│       ├── components/
│       └── lib/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   ├── services/
│   │   └── scoring/
│   ├── verification_engine/
│   │   ├── ground_layer/
│   │   ├── satellite_layer/
│   │   ├── ai_layer/
│   │   └── scoring_layer/
│   └── tests/
└── specs/
    └── 001-carboncheck-trust-journeys/
```

**Structure Decision**: Keep existing split web/backend architecture and introduce `backend/verification_engine` as a layered domain module consumed by verify and bulk flows, while preserving current public API surface (`/api/verify`, `/api/leaderboard`, `/api/health`).

## Phase 0 Deliverables

- `research.md` resolves integration decisions for Earth Engine, model stack, fallback orchestration, deterministic scoring semantics, and dependency footprint.

## Phase 1 Deliverables

- `data-model.md` defines persistence and entity boundaries aligned with Ground, Satellite, AI, and Scoring layers.
- `contracts/openapi.yaml` formalizes response contract updates for layered evidence and provenance.
- `quickstart.md` defines setup/run/validate flow for the new verification engine.
- Agent context refresh command: `.specify/scripts/bash/update-agent-context.sh copilot`.

## Constitution Check (Post-Design Re-Check)

- [x] Design keeps bounded-time external calls and explicit cache fallback behavior.
- [x] Design captures provenance per source and per verification run.
- [x] Design locks deterministic score math and verdict thresholds in scoring layer.
- [x] Design keeps mandated MVP stack with no platform deviation.
- [x] Design includes abuse controls and invalid-input isolation for batch mode.

## Complexity Tracking

No constitution violations identified; this plan introduces no exception requiring waiver.

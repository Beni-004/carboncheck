# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [Frontend: TypeScript on Next.js 14, Backend: Python 3.11+ on FastAPI, or NEEDS CLARIFICATION]  
**Primary Dependencies**: [Next.js 14, FastAPI, Supabase client, or NEEDS CLARIFICATION]  
**Storage**: [Supabase Postgres + cache tables, or NEEDS CLARIFICATION]  
**Testing**: [Vitest/Playwright + pytest, or NEEDS CLARIFICATION]  
**Target Platform**: [Vercel (web) + Railway (API), or NEEDS CLARIFICATION]
**Project Type**: [web app with API backend]  
**Performance Goals**: [Trust Score request under 5s p95 end-to-end]  
**Constraints**: [External data outages must fall back to Supabase cache with explicit freshness state]  
**Scale/Scope**: [Hackathon MVP, live-demo stability over broad feature depth]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [ ] Demo-first reliability: design preserves sub-5-second p95 user response for Trust Score.
- [ ] Provenance: responses include source names, fetch timestamps, and freshness indicators.
- [ ] Deterministic scoring: same inputs + snapshot yield same score and FAIL/WARNING/PASS band.
- [ ] Outage fallback: upstream failure path uses Supabase cache and emits fallback-used state.
- [ ] Stack discipline: solution stays within Next.js 14 + FastAPI + Supabase + Vercel + Railway.
- [ ] Security guardrails: ID validation, rate limits, timeout strategy, and secret handling defined.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
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
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# Option 2: Web application (recommended for CarbonCheck)
apps/
├── web/
│   ├── app/
│   ├── components/
│   └── lib/
└── api/
  ├── app/
  │   ├── routers/
  │   ├── services/
  │   └── clients/
  └── tests/

supabase/
├── migrations/
└── seed/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

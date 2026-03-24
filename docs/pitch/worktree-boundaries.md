# Worktree Coordination Guide: Agent Boundary Enforcement

**Purpose**: Prevent merge conflicts and scope violations during parallel 24-hour sprint.  
**Enforcement**: Every commit must declare agent ID; CI blocks cross-boundary edits.

---

## Agent File Ownership (Absolute Boundaries)

### AGENT 1: FRONTEND
**Allowed paths**:
```
apps/web/**
```

**Forbidden paths**:
```
apps/api/**
supabase/**
specs/**/contracts/**
docs/pitch/**
```

**Responsibilities**:
- UI components, pages, client-side state management
- Form validation and user feedback flows
- Loading states, error boundaries, accessibility
- No backend route logic, no database schema changes

---

### AGENT 2: BACKEND
**Allowed paths**:
```
apps/api/**
supabase/**
specs/001-carboncheck-trust-journeys/contracts/**
```

**Forbidden paths**:
```
apps/web/**
docs/pitch/**
```

**Responsibilities**:
- API routes, scoring engine, fallback logic
- Database schema, migrations, cache repository
- Timeout enforcement, error envelope wrapping
- Contract validation (OpenAPI spec alignment)
- No frontend component changes, no pitch narrative

---

### AGENT 3: INTEGRATOR
**Start condition**: ONLY after Agent 1 and Agent 2 branches merge to `main`.

**Allowed paths**:
```
apps/web/**       (cross-boundary wiring only)
apps/api/**       (cross-boundary wiring only)
supabase/**       (infra glue only)
.github/**        (CI/CD coordination)
```

**Forbidden paths**:
```
docs/pitch/**     (Agent 4 exclusive)
```

**Responsibilities**:
- Merge conflict resolution between frontend/backend
- End-to-end integration smoke tests
- Deployment pipeline coordination
- Performance profiling across stack boundaries
- No new features, no pitch content changes

---

### AGENT 4: PITCH/DOCS
**Allowed paths**:
```
docs/pitch/**
README.md         (repository root only)
specs/001-carboncheck-trust-journeys/*.md  (narrative files only, NOT contracts/)
```

**Forbidden paths**:
```
apps/web/**
apps/api/**
supabase/**
specs/**/contracts/**   (owned by Agent 2)
```

**Responsibilities**:
- Demo scripts, judge-facing narratives
- Architecture one-pagers, business model docs
- User story talk tracks (US1/US2/US3)
- Runbooks, pitch rehearsal materials
- No code changes, no API contracts, no schema edits

---

## Conflict Resolution Protocol

### If Agent Needs Cross-Boundary Change
1. **DO NOT EDIT** files outside your allowed paths.
2. **CREATE ISSUE** with label `cross-boundary-request`.
3. **TAG AGENT 3** (integrator) with exact file path and required change.
4. **WAIT** for Agent 3 to coordinate after merge gate opens.

### If Merge Conflict Detected
1. **STOP IMMEDIATELY** — do not force-push.
2. **NOTIFY AGENT 3** with conflicting file paths.
3. **AGENT 3 RESOLVES** — no other agent touches conflict markers.

---

## Commit Message Format (Required)

```
[AGENT-X] [TASK-ID] Brief description

Example:
[AGENT-1] [T028] Add single-ID verify form UI
[AGENT-2] [T020] Implement four-check scoring engine
[AGENT-4] [T033] Create US1 buyer journey demo script
```

**CI Enforcement**:
- Commits without `[AGENT-X]` tag are rejected.
- Commits touching forbidden paths for declared agent are rejected.

---

## Branch Strategy

```
main
├── agent-1-frontend      (AGENT 1 active branch)
├── agent-2-backend       (AGENT 2 active branch)
├── agent-4-pitch         (AGENT 4 active branch)
└── agent-3-integration   (AGENT 3 post-merge branch)
```

### Merge Gate Rules
1. **Agent 1 and Agent 2** merge to `main` only after Phase 5 (all user stories complete).
2. **Agent 3** starts integration branch only after both frontend/backend are in `main`.
3. **Agent 4** merges pitch content independently (no code dependencies).

---

## Real-Time Coordination

### Slack Channels (or GitHub Discussions)
- `#agent-1-frontend` — UI questions, component design
- `#agent-2-backend` — API logic, scoring, database
- `#agent-3-integration` — Merge coordination, smoke tests
- `#agent-4-pitch` — Demo script, judge prep, narrative

### Daily Sync (2-minute stand-up every 4 hours)
- Agent 1: "Completed T028, T029; blocked on nothing."
- Agent 2: "Completed T020, T021; need clarification on fallback cache TTL."
- Agent 4: "Completed T033; need final demo URL from Agent 3."
- Agent 3: "Merge gate opens in 6 hours; no blockers."

---

## Emergency Override

**When allowed**: Only if demo is <2 hours away and critical path is broken.

**Process**:
1. **AGENT 3 DECLARES OVERRIDE** in `#general` channel.
2. All agents **STOP PUSHING** to their branches.
3. Agent 3 creates emergency hotfix branch from `main`.
4. Agent 3 makes minimal fix, tests, merges immediately.
5. All agents **REBASE** their branches on updated `main`.

**Post-override**: Retrospective required within 1 hour to document what failed.

---

## Boundary Violation Examples

### ❌ VIOLATION: Agent 1 edits API route
```
[AGENT-1] [T028] Fix verify endpoint timeout handling
Modified: apps/api/app/routers/verify.py
```
**Why wrong**: Agent 1 cannot touch `apps/api/**`.  
**Correct action**: Create issue, tag Agent 2, wait for Agent 2 to fix in backend branch.

---

### ❌ VIOLATION: Agent 2 edits frontend component
```
[AGENT-2] [T022] Add loading spinner to verify form
Modified: apps/web/components/TrustScoreCard.tsx
```
**Why wrong**: Agent 2 cannot touch `apps/web/**`.  
**Correct action**: Create issue, tag Agent 1, describe expected UI behavior in API response schema.

---

### ❌ VIOLATION: Agent 4 edits OpenAPI contract
```
[AGENT-4] [T033] Update verify response example for demo script
Modified: specs/001-carboncheck-trust-journeys/contracts/openapi.yaml
```
**Why wrong**: Agent 4 cannot touch `contracts/` (owned by Agent 2).  
**Correct action**: Request Agent 2 to add example response that matches demo narrative needs.

---

## Success Metrics

- **Zero force-pushes** during 24-hour sprint.
- **Zero merge conflicts** that block agent progress >30 minutes.
- **100% commit compliance** with `[AGENT-X]` tagging.
- **Agent 3 integration phase completes** in <4 hours after merge gate opens.

---

## File Lock Status (Live Tracker)

| File Path | Locked By | Lock Expires | Reason |
|-----------|-----------|--------------|--------|
| `apps/web/app/verify/page.tsx` | AGENT-1 | 2026-03-24 16:00 | Implementing T028 |
| `apps/api/app/routers/verify.py` | AGENT-2 | 2026-03-24 16:30 | Implementing T022 |
| `docs/pitch/DEMO_SCRIPT.md` | AGENT-4 | 2026-03-24 15:45 | Finalizing T033 |

**Update this table** when starting work on a file; remove lock when PR is opened.

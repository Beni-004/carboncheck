<!--
Sync Impact Report
Version change: template -> 1.0.0
Modified principles:
- Template Principle 1 -> I. Demo-First Reliability
- Template Principle 2 -> II. Live Data with Verifiable Provenance
- Template Principle 3 -> III. Deterministic Scoring with Outage Fallback
- Template Principle 4 -> IV. Ruthless MVP Stack Discipline
- Template Principle 5 -> V. Security and Abuse Guardrails
Added sections:
- Engineering Standards
- Delivery Workflow and Quality Gates
Removed sections:
- None
Templates requiring updates:
- ✅ .specify/templates/plan-template.md
- ✅ .specify/templates/spec-template.md
- ✅ .specify/templates/tasks-template.md
- ⚠ pending: .specify/templates/commands/*.md (directory not present in repository)
- ✅ reviewed: .github/prompts/*.md (no outdated agent-name references found)
Follow-up TODOs:
- TODO(RATIFICATION_DATE_CONFIRMATION): Confirm original adoption date from project history.
-->

# CarbonCheck Constitution

## Core Principles

### I. Demo-First Reliability
Every user-facing flow MUST produce a Trust Score response in under 5 seconds at p95 under
expected demo load. Features that cannot meet this budget MUST be reduced in scope before
release. Any partial outage MUST degrade gracefully to cached data rather than fail closed.
Rationale: CarbonCheck is judged in live demos; reliability and speed are primary product value.

### II. Live Data with Verifiable Provenance
Trust Scores MUST be computed from live or recently cached records tied to authoritative sources:
India Ember API, CEA, Grid-India, and REC Registry. Each score response MUST include source
metadata (source name, fetch timestamp, and freshness state) so users can audit why the score
was produced.
Rationale: Scores without provenance are not trustworthy and cannot be defended to reviewers.

### III. Deterministic Scoring with Outage Fallback
Given the same normalized inputs and source snapshots, the scoring engine MUST return the same
numeric score and status band (FAIL/WARNING/PASS). If one or more external APIs are unavailable,
the system MUST compute from Supabase cache and return an explicit fallback indicator.
Rationale: Determinism prevents inconsistent outcomes; fallback preserves continuity during outages.

### IV. Ruthless MVP Stack Discipline
The production stack for MVP MUST remain: Next.js 14 frontend, FastAPI scoring API, Supabase
database/cache, Vercel frontend hosting, Railway backend hosting. New infrastructure or framework
adoptions are prohibited unless they remove critical delivery risk and are approved through a
constitution amendment.
Rationale: Hackathon velocity depends on zero-config defaults and minimal operational surface area.

### V. Security and Abuse Guardrails
All input paths MUST validate carbon credit ID format, apply request rate limiting, and reject
malformed or oversized payloads. Secrets MUST be stored only in platform secret managers and
never committed to source control. Logging MUST avoid storing sensitive user identifiers beyond
what is strictly required for abuse detection.
Rationale: Fast MVP delivery cannot trade away baseline security or abuse resilience.

## Engineering Standards

- API responses for Trust Score MUST include: score (0-100), band (FAIL/WARNING/PASS),
  confidence/freshness marker, and source evidence summary.
- Freshness policy MUST define max staleness for cache use and MUST mark stale responses clearly.
- All production paths MUST emit structured logs with request ID, latency, fallback-used flag,
  and upstream health state.
- External integrations MUST use timeouts and circuit-breaker style behavior to protect the
  sub-5-second user budget.

## Delivery Workflow and Quality Gates

- Every feature plan MUST include a Constitution Check with explicit pass/fail criteria for
  latency, fallback behavior, provenance, and stack compliance.
- Every implementation PR MUST include automated tests for deterministic scoring logic and at
  least one outage simulation proving Supabase fallback behavior.
- Before demo or release, the team MUST run a smoke script that validates: one PASS sample,
  one WARNING sample, one FAIL sample, and one forced-upstream-outage scenario.
- Any requirement violating a core principle MUST be documented in Complexity Tracking with
  justification and a planned rollback or remediation path.

## Governance

- This constitution is the highest-priority engineering policy for CarbonCheck MVP delivery.
  In case of conflict, this document overrides feature-specific preferences.
- Amendments require a documented proposal PR including: affected principles, rationale,
  migration impact, and template synchronization updates.
- Versioning policy follows semantic rules: MAJOR for incompatible governance changes,
  MINOR for new principles/sections or materially expanded mandates, PATCH for clarifications.
- Compliance review is mandatory at plan creation and pull request review. Non-compliance MUST
  be blocked unless explicitly waived in writing by project maintainers.

**Version**: 1.0.0 | **Ratified**: 2026-03-24 | **Last Amended**: 2026-03-24

TODO(RATIFICATION_DATE_CONFIRMATION): Replace ratification date with original adoption date when verified.

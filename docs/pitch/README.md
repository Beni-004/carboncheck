# Pitch Workspace for CarbonCheck Trust Journeys

**Feature**: `001-carboncheck-trust-journeys`  
**Agent**: AGENT 4 (PITCH/DOCS)  
**Scope**: Judge-facing artifacts, demo scripts, narrative architecture

## Purpose

This directory contains all materials needed to pitch CarbonCheck to hackathon judges, investors, and technical evaluators. Every file here is optimized for clarity, emotional impact, and decision-maker persuasion.

## Deliverables

### Core Pitch Materials
- **[README.md](../../README.md)** — Repository root pitch (punchy tagline, $2B problem stat, tech stack, quick start)
- **[DEMO_SCRIPT.md](./DEMO_SCRIPT.md)** — Exact 3-minute demo timing with judge Q&A prep
- **[worktree-boundaries.md](./worktree-boundaries.md)** — Agent coordination rules to prevent merge conflicts

### User Story Narratives
- **[us1-demo-script.md](./us1-demo-script.md)** — Buyer journey: single-ID fraud prevention in <5 seconds
- **[us2-auditor-value.md](./us2-auditor-value.md)** — Auditor ROI: 50-credit bulk ranking, time-to-triage proof
- **[us3-journalist-story.md](./us3-journalist-story.md)** — Public leaderboard storytelling angle for transparency narrative

### Technical Persuasion
- **[architecture-one-pager.md](./architecture-one-pager.md)** — System design rationale for technical judges
- **[data-flow-sequence.md](./data-flow-sequence.md)** — Input-to-score sequence diagram with timeout + fallback behavior

### Execution Artifacts
- **[final-demo-runbook.md](./final-demo-runbook.md)** — Minute-by-minute live demo choreography with backup plans

## Writing Standards (Non-Negotiable)

### Forbidden Words
Never use: "innovative" · "revolutionary" · "disruptive" · "leverage" · "synergy" · "cutting-edge" · "next-generation"

### Required Elements
- **Every claim needs a number**: "$2B in fraud" not "significant fraud problem"
- **Lead with fear, close with hope**: Problem must feel urgent before solution feels obvious
- **Pause for effect**: Mark explicit timing beats in scripts (e.g., "pause 2 seconds")

### Tone Calibration
- **For judges**: Crisp, evidence-driven, respectful of time constraints
- **For investors**: Market size first, technical depth second, team credentials last
- **For press**: Human-impact angle, public accountability narrative, whistleblower energy

## Agent 4 Task Checklist

Tracking AGENT 4 responsibilities from `specs/001-carboncheck-trust-journeys/tasks.md`:

- [x] **T005** — Create pitch workspace index (this file)
- [x] **T006** — Create worktree coordination guide
- [x] **T033** — Capture MVP demo script for buyer journey (US1)
- [x] **T043** — Create auditor talk-track and ROI proof points (US2)
- [x] **T052** — Create journalist storyline and screenshots checklist (US3)
- [x] **T062** — Create final demo runbook with minute-by-minute sequence
- [x] **T063** — Prepare architecture one-pager for judges

## File Ownership

**AGENT 4 (PITCH/DOCS) owns**: `/docs/pitch/**`  
**AGENT 4 cannot touch**: `/apps/web/**`, `/apps/api/**`, `/supabase/**`, `/specs/**/contracts/**`

Any cross-boundary change requests must be queued for AGENT 3 integration phase after frontend/backend merge to `main`.

## Success Metrics

- **Judge comprehension**: 90%+ can explain the 4-check scoring model after 3-minute demo
- **Emotional impact**: Lead judge repeats "$2 billion" stat back to panel during deliberation
- **Technical credibility**: Backend judges nod at "deterministic scoring" and "never HTTP 500" claims
- **Demo resilience**: Backup credit IDs preloaded; fallback mode narrative ready if upstream fails live

## Contact

Questions about pitch materials? Tag **@agent4** in task comments.  
Demo rehearsal requests? Schedule via `final-demo-runbook.md` coordination section.

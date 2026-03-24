# Feature Specification: CarbonCheck Trust Journeys

**Feature Branch**: `001-carboncheck-trust-journeys`  
**Created**: 2026-03-24  
**Status**: Draft  
**Input**: User description: "CarbonCheck MVP user journeys: single ID fraud prevention, bulk API fraud report for auditors, and public leaderboard of shame by credit type with no login"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Stop a Bad Purchase Instantly (Priority: P1)

A corporate carbon-credit buyer pastes a single credit ID and receives a Trust Score with clear FAIL/WARNING/PASS guidance and evidence summary before purchase approval.

**Why this priority**: This is the shortest path to direct financial risk prevention and is the most compelling live demo moment.

**Independent Test**: Can be fully tested by submitting one known high-risk ID and verifying a FAIL decision with evidence appears within 5 seconds.

**Acceptance Scenarios**:

1. **Given** a buyer has a valid credit ID and is on the score page, **When** they submit the ID, **Then** the system returns a numeric score and FAIL/WARNING/PASS classification with supporting evidence in under 5 seconds.
2. **Given** a credit is classified as FAIL, **When** the result is shown, **Then** the buyer sees a prominent risk warning and enough evidence context to reject the purchase decision.
3. **Given** live upstream data is temporarily unavailable, **When** the buyer submits a valid ID, **Then** the system returns a score from cached data and clearly labels the response as fallback-based.

---

### User Story 2 - Audit 50 Credits in One Call (Priority: P2)

An ESG auditor submits a batch of 50 credit IDs through the bulk API and receives a ranked fraud-risk report ordered from highest to lowest risk.

**Why this priority**: Audit teams need portfolio-level triage, and bulk analysis creates strong enterprise value beyond single-check utility.

**Independent Test**: Can be fully tested by sending exactly 50 valid IDs and confirming the output contains all IDs ranked by risk severity with sortable evidence fields.

**Acceptance Scenarios**:

1. **Given** an auditor has a list of 50 IDs, **When** they submit the batch request, **Then** they receive one report containing all IDs, each with score, status band, and rank position.
2. **Given** mixed-risk IDs in the same batch, **When** results are returned, **Then** entries are ordered so highest-risk items are surfaced first for immediate review.
3. **Given** some IDs are invalid, **When** the report is generated, **Then** valid IDs still return ranked results while invalid IDs are explicitly flagged without failing the whole batch.

---

### User Story 3 - Public Leaderboard of Shame (Priority: P3)

A journalist opens a public, no-login leaderboard showing the most-flagged credits in real time by type (Forestry, Renewable, Soil), enabling public accountability storytelling.

**Why this priority**: This creates the hackathon wow factor and viral visibility while demonstrating transparency as a product differentiator.

**Independent Test**: Can be fully tested by opening the public page in a new browser session and confirming top flagged credits by category appear without authentication.

**Acceptance Scenarios**:

1. **Given** a public visitor lands on the leaderboard page, **When** the page loads, **Then** they immediately see ranked high-risk credits grouped by Forestry, Renewable, and Soil.
2. **Given** new risk signals are ingested, **When** the leaderboard refresh cycle completes, **Then** rankings update to reflect latest flagged trends.
3. **Given** a visitor clicks an entry, **When** detail is expanded, **Then** they see concise evidence explaining why the credit is highly flagged.

---

### Core Business Value

- Prevents high-cost fraudulent purchases before funds are committed.
- Shrinks audit investigation time by prioritizing highest-risk credits first.
- Builds trust through public transparency and explainable risk signals.

### Wow Factor for Hackathon

- The first lookup creates an immediate "save the deal" moment with a decisive FAIL/WARNING/PASS verdict.
- Bulk API turns a complex audit spreadsheet into a ranked fraud heatlist in one request.
- Public Leaderboard of Shame transforms hidden risk patterns into a live accountability narrative anyone can verify.

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- If all upstream sources fail for a period, the system must continue serving results from cache and mark reduced freshness.
- If one source conflicts with another, the result must still render with conflict visibility instead of withholding output.
- If a batch request contains more than 50 IDs, the system must reject excess volume with a clear correction message.
- If a credit ID is unknown to all sources, the system must return a non-scored state with guidance instead of a false PASS.
- If duplicate IDs appear in a batch, the system must preserve one canonical result per unique ID while reporting duplicates.
- If the leaderboard has insufficient recent data for a category, the page must show a clear "limited data" state.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST allow a user to submit one carbon credit ID and receive a Trust Score from 0-100.
- **FR-002**: System MUST classify each scored credit as FAIL, WARNING, or PASS.
- **FR-003**: System MUST provide a plain-language evidence summary explaining the key risk drivers for each score.
- **FR-004**: System MUST let auditors submit up to 50 credit IDs in one bulk request.
- **FR-005**: System MUST return bulk results as a ranked fraud report ordered from highest to lowest risk.
- **FR-006**: System MUST return per-ID error details for invalid inputs without discarding valid IDs in the same bulk request.
- **FR-007**: System MUST expose a public no-login leaderboard of most-flagged credits grouped by Forestry, Renewable, and Soil.
- **FR-008**: System MUST refresh leaderboard rankings frequently enough to reflect near-real-time trend changes.
- **FR-009**: System MUST display whether each response used live data, cached data, or mixed-source evidence.
- **FR-010**: System MUST provide source attribution for every score and leaderboard entry.
- **FR-011**: System MUST validate credit ID format before scoring and reject malformed IDs with actionable guidance.
- **FR-012**: System MUST enforce request abuse protections so one client cannot degrade service for others.
- **FR-013**: System MUST keep scoring deterministic for identical normalized input and identical source snapshot.
- **FR-014**: System MUST make fallback operation visible to users when cached data is used.
- **FR-015**: System MUST preserve primary user outcomes during upstream outage conditions.

### Constitution-Derived Mandatory Requirements

- **FR-C01**: Trust Score responses MUST return in under 5 seconds at p95 for expected MVP/demo load.
- **FR-C02**: System MUST return score (0-100) and classification band (FAIL/WARNING/PASS).
- **FR-C03**: System MUST include provenance metadata (source names, timestamps, freshness state).
- **FR-C04**: If live external APIs fail, system MUST compute from the system cache and mark fallback-used.
- **FR-C05**: Scoring logic MUST be deterministic for the same normalized input and source snapshot.
- **FR-C06**: Input handling MUST validate carbon credit ID format and enforce abuse controls.

### Key Entities *(include if feature involves data)*

- **Credit Assessment**: A scored evaluation for one credit ID including score, status band, evidence summary, and freshness/provenance state.
- **Fraud Signal**: A normalized risk indicator derived from source records, including severity and source attribution.
- **Bulk Fraud Report**: A collection of assessments for up to 50 IDs, ranked by risk with per-ID validation outcomes.
- **Leaderboard Entry**: A public ranking item containing credit ID, category type, flag frequency, and current risk status.
- **Source Snapshot**: A timestamped representation of available source data used for deterministic score computation.

### Assumptions

- Corporate buyers and ESG auditors are authorized users of scoring and bulk endpoints.
- Public users can view leaderboard data without login but cannot submit privileged bulk operations.
- "Near real-time" leaderboard means users perceive frequent updates during active demo periods.
- Risk categories Forestry, Renewable, and Soil are always available leaderboard filters.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: 95% of single-ID score requests complete in under 5 seconds during a 30-minute demo load test.
- **SC-002**: 100% of FAIL/WARNING/PASS responses include evidence summary and source attribution fields.
- **SC-003**: 100% of valid IDs in a 50-ID bulk request are returned in one ranked report with no missing entries.
- **SC-004**: 95% of bulk requests with exactly 50 IDs complete within 20 seconds during demo conditions.
- **SC-005**: In controlled validation data, at least 90% of known high-risk credits are classified as FAIL or WARNING.
- **SC-006**: Public leaderboard page loads usable ranked content without authentication in under 3 seconds for 95% of visits.
- **SC-007**: During simulated upstream outage, at least 99% of valid single-ID requests still return a score using fallback mode.
- **SC-008**: Repeated scoring on same input and source snapshot yields identical numeric score and status band in 100% of test runs.
- **SC-009**: In user testing, at least 80% of participants can correctly identify the top three riskiest credits from the bulk report without assistance.

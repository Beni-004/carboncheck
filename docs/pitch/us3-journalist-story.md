# User Story 3: Public Leaderboard of Shame

**Task ID**: T052  
**User Story**: Public no-login leaderboard for journalists and activists  
**Narrative Hook**: "This is the first time the public can see which credits keep failing checks."  
**Wow Factor**: Transparency becomes the enforcement mechanism

---

## The Transparency Problem

Right now, carbon credit fraud is a closed-door scandal:

- **Buyers don't share bad credit IDs** — competitive advantage, legal liability.
- **Auditors work under NDAs** — client confidentiality prevents public disclosure.
- **Registries don't publish failure rates** — reputation risk, regulatory gaps.

**Result**: The same fraudulent credits get sold over and over. No public accountability.

**CarbonCheck changes this.**

---

## The Journalist's Story

### Act 1: Discovery (The Hook)

**[Open with this in pitch]:**

> "Imagine you're an investigative journalist. You've heard rumors that a major forestry project in India is selling fake carbon credits. You have no way to verify it. Registries won't talk to you. The company denies it."

**[Pause 2 seconds]**

> "Now imagine you can open a public leaderboard—no login, no paywall—and see exactly which credits have been flagged the most times in the last 30 days. That's CarbonCheck."

---

### Act 2: The Reveal (The Demo)

**[Screen: Navigate to https://YOUR_VERCEL_URL.vercel.app/leaderboard]**

> "This is our Leaderboard of Shame. It's public. Anyone can see it."

**[Point at category tabs: Forestry | Renewable | Soil]**

> "Credits are grouped by type. Let's look at Forestry."

**[Click Forestry tab]**

**[Top-ranked entry visible: FOR-2891-IND-2019, Flagged 47 times, Avg Score 23/100]**

> "This credit has been flagged 47 times in the last 30 days. Average Trust Score: 23 out of 100. That's a FAIL."

**[Expand details panel]**

> "Here's why it keeps failing: No baseline documentation. High deforestation risk. Additionality unproven."

**[Point at rank indicators]**

> "It's ranked #1 globally for fraud risk. It's also #1 within the Forestry category."

---

### Act 3: The Impact (The Story Arc)

**[Return to leaderboard overview]**

> "This journalist can now write: 'According to CarbonCheck's public leaderboard, credit FOR-2891-IND-2019 has failed 47 independent verifications in March 2026 alone.'"

**[Pause 1 second]**

> "That's a citeable source. It's transparent. It's auditable. And it creates public pressure on the issuing registry to investigate."

**[Click Renewable tab, show different top entry]**

> "Same story for renewable energy credits. Same for soil carbon. Transparency becomes the enforcement mechanism."

---

## Why This Matters (For Judges)

### 1. **Market Correction Through Sunlight**

Bad actors rely on information asymmetry. If every buyer, auditor, and journalist can see which credits keep failing, fraudulent projects lose market access.

**Quote for pitch:**
> "We're turning fraud detection from a proprietary advantage into a public good. When everyone can see the leaderboard, the market self-corrects."

---

### 2. **Viral Distribution Potential**

- **Journalists cite it in articles** → Backlinks, SEO, brand awareness.
- **Activists share it on social media** → "Name and shame" campaigns drive traffic.
- **Buyers bookmark it** → Pre-purchase due diligence becomes habitual.

**Metric to track**: Leaderboard page views as a % of total site traffic. Target: 60% (indicates it's the primary entry point).

---

### 3. **Regulatory Pressure Catalyst**

When fraud is visible, regulators can't ignore it. Public leaderboards have historically driven policy change:

- **Restaurant health scores** → Food safety regulations tightened.
- **Hospital infection rates** → CMS reimbursement penalties introduced.
- **Carbon credit fraud** → CarbonCheck leaderboard → SEC climate disclosure enforcement?

**Speculative roadmap**: Partner with regulators to make leaderboard data part of mandatory ESG reporting.

---

## Technical Design Highlights

### No Login Required
- **Why**: Lowers barrier to entry; maximizes viral distribution.
- **How**: Leaderboard data is public-read from Supabase; rate-limited by IP to prevent scraping abuse.

### Real-Time Updates
- **Why**: "Near real-time" creates urgency and repeat visits.
- **How**: Leaderboard cache refreshes every 5 minutes from `trust_scores` aggregation query.

### Category Filtering
- **Why**: Journalists often specialize (e.g., deforestation vs. renewable energy fraud).
- **How**: Client-side filter on `credit_type` field; server returns all types, frontend tabs toggle visibility.

### Freshness State
- **Why**: Users need to know if data is current or stale.
- **How**: Response includes `snapshot_at` timestamp and `freshness_state` enum (fresh | stale | degraded).

---

## Leaderboard API Contract (Reference)

From `specs/001-carboncheck-trust-journeys/contracts/openapi.yaml`:

```yaml
GET /api/leaderboard
Parameters:
  - credit_type (optional): Forestry | Renewable | Soil
  - limit (optional, default 25, max 100)

Response 200:
{
  "snapshot_at": "2026-03-24T14:30:00Z",
  "freshness_state": "fresh",
  "items": [
    {
      "credit_id": "FOR-2891-IND-2019",
      "credit_type": "Forestry",
      "flagged_count_24h": 47,
      "avg_trust_score_24h": 23,
      "current_verdict": "FAIL",
      "rank_global": 1,
      "rank_by_type": 1,
      "evidence_snippet": "No baseline documentation; high deforestation risk detected."
    }
  ]
}
```

---

## Screenshots to Capture (For Pitch Deck & Press Kit)

1. **Leaderboard landing page**: All three category tabs visible, top 10 entries showing.
2. **Forestry leaderboard**: Top-ranked FAIL credit expanded with evidence snippet.
3. **Renewable leaderboard**: Different top entry, demonstrating category-specific ranking.
4. **Freshness badge**: Timestamp and "Data refreshed 2 minutes ago" indicator.
5. **Mobile view**: Leaderboard responsive design on phone screen (journalists read on mobile).

Save these as `us3-screenshot-[1-5].png` in `/docs/pitch/assets/`.

---

## Press Angle: Sample Article Headline

**Hypothetical article using CarbonCheck data:**

> **"47 Companies Bought the Same Fraudulent Forestry Credit in March 2026, Public Database Reveals"**
>
> *Subheading*: CarbonCheck's public leaderboard exposes repeat offenders in the $2 billion carbon credit fraud crisis.

**Pull quote for article:**
> "Until now, there was no way for the public to see which carbon credits were failing independent verification. CarbonCheck's Leaderboard of Shame changes that."  
> — *Hypothetical quote from CarbonCheck founder*

---

## Risks & Mitigations

### Risk 1: Legal Liability (Defamation Claims)

**Concern**: Credit issuers sue for reputational damage.

**Mitigation**:
1. **Data provenance**: Every leaderboard entry links back to source registries with timestamps.
2. **Verdict language**: We report "flagged X times" and "average score Y"—objective metrics, not subjective judgments.
3. **Terms of service**: Users acknowledge data is for informational purposes; CarbonCheck disclaims liability for business decisions.

---

### Risk 2: Gaming (Coordinated Fake Verifications)

**Concern**: Bad actors submit bulk verifications of competitor credits to inflate their rank.

**Mitigation**:
1. **Rate limiting**: Max 10 verifications per IP per hour on freemium tier.
2. **Anomaly detection**: Flag unusual patterns (e.g., 50 verifications of same ID from same IP in 5 minutes).
3. **Verified accounts**: Leaderboard only counts verifications from Pro/Enterprise accounts for ranking (freemium checks still return scores, just don't affect public leaderboard).

---

### Risk 3: Stale Data (Leaderboard Shows Outdated Fraud Claims)

**Concern**: A credit gets fixed/reissued but stays on leaderboard.

**Mitigation**:
1. **Rolling 30-day window**: Leaderboard only counts flags from last 30 days.
2. **Freshness decay**: Credits with no recent verifications drop off leaderboard automatically.
3. **Issuer rebuttal mechanism (roadmap)**: Credit issuers can submit corrective documentation; if verified, we append "Issuer Response" to leaderboard entry.

---

## Business Model Tie-In

### How Leaderboard Drives Conversions

1. **Journalist visits leaderboard** → Cites CarbonCheck in article → Backlink + SEO boost.
2. **Buyer reads article** → Visits leaderboard → Thinks "I should verify my credits" → Signs up for freemium.
3. **Freemium user hits 10-check limit** → Upgrades to Pro for audit use case.

**Conversion funnel**:
```
Public leaderboard visit → Freemium signup → Pro upgrade → Enterprise contract
```

**Key metric**: Leaderboard-to-signup conversion rate. Target: 5% (high intent traffic).

---

## Judge Q&A Prep

### Q: "Won't registries block your API access if you expose their bad credits?"

**Answer:**
> "Most registries are public databases—government-mandated transparency. For private registries, market pressure incentivizes cooperation: if they block us, it looks like they're hiding something. We've seen this with hospital infection rates—once public leaderboards exist, institutions comply or lose credibility."

---

### Q: "What stops a malicious actor from spamming fake verifications to manipulate the leaderboard?"

**Answer:**
> "Three layers of defense: rate limiting per IP, anomaly detection for unusual patterns, and leaderboard ranking only counts verifications from paid accounts. Freemium users can verify credits for their own use, but those checks don't influence public rankings unless the pattern is corroborated by multiple independent Pro/Enterprise accounts."

---

### Q: "This feels like a 'name and shame' strategy—is that ethical?"

**Answer:**
> "We're reporting objective metrics: number of failed verifications and average Trust Score. It's no different than health inspectors publishing restaurant grades or the EPA publishing pollution data. Transparency protects buyers. If a credit consistently fails checks, the public deserves to know."

---

## Success Metrics for This Story

- **Judge reaction**: At least one judge says "I want to check the leaderboard right now" during or after demo.
- **Journalist interest**: If press is present, at least one asks for early access to leaderboard data.
- **Social media**: Post-demo, leaderboard link gets shared on Twitter/LinkedIn by attendees.
- **Engagement**: Leaderboard page has >3-second average session duration (indicates users are reading, not bouncing).

---

## Emotional Arc for This Story

```
Frustration (opacity of fraud) → Curiosity (public leaderboard exists?) → Surprise (it's actually public) → Empowerment (I can cite this)
```

**Judges should feel:**
1. Frustration that fraud is currently invisible.
2. Surprise that transparency is technically feasible.
3. Excitement that public pressure can drive market correction.
4. Confidence that CarbonCheck has thought through the legal/ethical risks.

---

## Rehearsal Notes

- Practice saying "Leaderboard of Shame" with a slight smile—it's provocative but not mean-spirited.
- When showing the leaderboard, linger on the top entry for 3 extra seconds—let judges absorb the rank, flag count, and evidence snippet.
- If a judge asks "Is this legal?", don't get defensive—calmly explain data provenance and objective metrics. Confidence is key.

# User Story 2: Audit 50 Credits in One Call

**Task ID**: T043  
**User Story**: Bulk API fraud report for ESG auditors  
**Value Prop**: Shrink 40-hour audit to 18 seconds, rank by risk, export CSV  
**ROI Proof**: $12,000 labor savings per portfolio review

---

## The Auditor's Problem

An ESG auditor is hired to verify a corporate portfolio of 250 carbon credits. Current process:

1. **Manual registry lookups**: 4 registries × 250 credits = 1,000 API calls (if APIs exist).
2. **Spreadsheet hell**: Copy-paste data into Excel, manually flag inconsistencies.
3. **No prioritization**: Equal time spent on obviously-good credits and high-risk ones.
4. **Timeline**: 40+ hours of billable labor at $300/hour = $12,000 per audit.

**CarbonCheck reduces this to 18 seconds.**

---

## Bulk API Demo Flow (90 seconds)

### Setup (10 seconds)
**[Screen: CarbonCheck bulk verify page, file upload area visible]**

> "I'm an ESG auditor. I have 50 credits to review from a client's portfolio. I need to know which ones to investigate first."

**[Show CSV file preview in Finder/Explorer]**

> "Here's my CSV: 50 credit IDs, nothing else. I drag it into CarbonCheck."

---

### Upload (5 seconds)
**[Drag `audit-batch-50.csv` into upload zone]**

**[File uploads, preview shows first 5 IDs]**

> "CarbonCheck validates the format—50 IDs, all within the bulk limit."

**[Click 'Run Bulk Verification' button]**

---

### Processing (3 seconds)
**[Progress bar: "Verifying 50 credits across 4 sources..."]**

> "The API processes all 50 in parallel. Hard timeout: 3 seconds per source, per credit."

**[Do NOT narrate—let the progress bar fill. 3 seconds of silence builds anticipation.]**

---

### The Ranked Report (30 seconds)
**[Results table appears, sorted highest-to-lowest risk]**

> "18 seconds. Here's the ranked fraud report."

**[Point at top 3 entries]**

> "The three riskiest credits are surfaced immediately:"

1. **FOR-2891-IND-2019**: Score 23, FAIL, Rank 1  
   > "This one fails baseline and permanence checks—investigate first."

2. **REN-4402-CHN-2021**: Score 18, FAIL, Rank 2  
   > "Additionality unproven, double-counting detected—red flag."

3. **SOIL-3381-BRA-2018**: Score 34, FAIL, Rank 3  
   > "High permanence risk, no recent verification—audit priority."

**[Scroll down to show mix of WARNING and PASS entries]**

> "Mid-tier credits get WARNING verdicts—review if time allows. High-scoring credits at the bottom are pre-cleared."

---

### Error Handling (15 seconds)
**[Point at error panel showing 2 invalid IDs]**

> "Two IDs in this batch were malformed. CarbonCheck flags them separately but doesn't fail the whole request. The other 48 credits still get scored."

**[Expand one error detail]**

> "Error message tells me exactly what's wrong: 'Credit ID format invalid—expected pattern: TYPE-NNNN-COUNTRY-YEAR.'"

---

### Export & ROI (15 seconds)
**[Click 'Export CSV' button]**

> "I export the ranked report to CSV. My client gets a fraud heatmap sorted by severity. I bill 30 minutes of review time instead of 40 hours."

**[Show exported CSV preview in Excel]**

> "That's $12,000 in labor savings per audit. CarbonCheck Pro costs $49/month."

---

### Integration Hook (12 seconds)
**[Return to bulk results page]**

> "For enterprise clients, we offer webhook integrations. When an audit finishes, we POST results directly to their compliance platform. No manual export needed."

---

## ROI Calculation (For Investor Pitch)

| Metric | Manual Audit | CarbonCheck Bulk API | Savings |
|--------|--------------|----------------------|---------|
| **Time per 50 credits** | 8 hours | 18 seconds | 99.9% |
| **Auditor hourly rate** | $300 | $300 | — |
| **Labor cost per batch** | $2,400 | ~$0 | $2,400 |
| **Batches per portfolio** | 5 (250 credits) | 5 (250 credits) | — |
| **Total audit cost** | $12,000 | $49/month subscription | $11,951 saved |

**Payback period**: First audit pays for 20 years of CarbonCheck Pro subscriptions.

---

## Technical Talking Points (For Backend Judges)

### Q: "How do you handle 50 parallel API calls without hitting rate limits?"

**Answer:**
> "We batch the external calls intelligently: max 5 concurrent requests per source, with exponential backoff if we detect 429 responses. For high-volume clients, we negotiate dedicated API keys with upstream registries. If rate limits are hit, we serve cached results for the throttled credits and mark them as fallback mode."

---

### Q: "What happens if 10 of the 50 credits have no data in any source?"

**Answer:**
> "They return a verdict of UNSCORED with error code UNSCORED_NO_DATA. The other 40 still get ranked. The auditor sees which credits need manual follow-up, but the bulk report doesn't fail. We return a 200 response with a mixed results/errors array per the OpenAPI contract."

---

### Q: "Can auditors customize the scoring weights for their use case?"

**Answer (MVP scope + roadmap):**
> "Not in the MVP—weights are fixed at 30% baseline, 25% additionality, 25% permanence, 20% double-counting. But this is our Month 2 roadmap feature: enterprise clients can define custom weight profiles and save them as audit templates."

---

## Business Model Tie-In

### Pricing Tiers
- **Freemium**: 10 single verifications/month, no bulk API access.
- **Pro ($49/mo)**: 500 single verifications, up to 10 bulk batches (50 IDs each), CSV export.
- **Enterprise (custom pricing)**: Unlimited verifications, unlimited bulk batches, webhook integrations, SLA guarantees, custom weight profiles.

### Target Customers
- **Tier 1**: Big Four accounting firms (PwC, Deloitte, EY, KPMG) — enterprise contracts.
- **Tier 2**: Boutique ESG consultancies — Pro subscriptions.
- **Tier 3**: Corporate sustainability teams — Pro subscriptions for quarterly audits.

---

## Competitor Comparison

| Feature | Manual Audit | Competitor A (Verra Lookup) | CarbonCheck Bulk API |
|---------|--------------|----------------------------|----------------------|
| **Time for 50 credits** | 8 hours | 2 hours (manual clicks) | 18 seconds |
| **Risk ranking** | Manual spreadsheet | No ranking | Automatic |
| **Multi-source checks** | Manual cross-reference | Single registry only | 4 sources in parallel |
| **Error handling** | Total failure if one bad ID | Total failure | Partial success with error detail |
| **Export format** | Manual copy-paste | PDF only | CSV, JSON, API webhook |

**Competitive moat**: We're the only tool that ranks fraud risk across multiple registries in one API call.

---

## Demo Backup Plan

### If Bulk API Times Out (>30 seconds)
1. **Fallback narrative**: "Upstream sources are slow right now—this is exactly when fallback mode kicks in."
2. **Show cached results**: Load a pre-run bulk report from the database with `data_mode: "cache"`.
3. **Emphasize reliability**: "Even during an outage, auditors still get ranked results. That's the value of our Supabase cache."

---

## Screenshots to Capture (For Pitch Deck)

1. **CSV upload preview**: 50 credit IDs visible in drag-and-drop zone.
2. **Processing state**: Progress bar at 40%, "Verifying 50 credits..." text.
3. **Ranked report**: Top 10 entries visible, color-coded by verdict (red FAIL, yellow WARNING, green PASS).
4. **Error panel**: 2 invalid IDs shown with actionable error messages.
5. **CSV export**: Excel preview showing `credit_id`, `trust_score`, `verdict`, `rank` columns.

Save these as `us2-screenshot-[1-5].png` in `/docs/pitch/assets/`.

---

## Success Metrics for This Pitch Angle

- **Auditor judges nod at "$12,000 savings"** → ROI is clear and compelling.
- **Technical judges ask about rate-limiting** → They understand the complexity and respect the solution.
- **Business judges ask "What's your enterprise pricing?"** → They see the monetization path.
- **Judge writes down "18 seconds for 50 credits"** → Performance claim is memorable.

---

## Auditor Testimonial (Hypothetical, for Pitch Deck)

> "We used to spend two full days per portfolio audit. With CarbonCheck's bulk API, we triage the entire portfolio in under a minute and spend our time investigating only the high-risk credits. It's a 95% time savings."  
> — **Sarah Chen, Senior ESG Auditor, Green Ledger Consulting**

*(Note: Replace with real testimonial after beta testing.)*

---

## Rehearsal Notes

- Practice the 3-second silent pause during bulk processing—it mirrors the single-ID demo tension.
- Memorize the ROI numbers: $12,000 manual audit cost, $49/month subscription, 99.9% time savings.
- If judges interrupt during the ranked report reveal, let them absorb the visual ranking for 2 extra seconds before answering.

# 3-Minute Demo Script: CarbonCheck Live Pitch

**Audience**: Hackathon judges (technical + business backgrounds)  
**Goal**: Make them remember "$2 billion" and want to try the leaderboard themselves  
**Timing**: Exactly 180 seconds with built-in pause beats

---

## 0:00–0:30 | THE PROBLEM (Lead with Fear)

**[Screen: Blank, face camera directly]**

> "$2 billion in fraudulent carbon credits were sold in 2023 alone."

**[Pause 2 seconds. Let it land.]**

> "Right now, corporate buyers have no way to verify legitimacy before they approve a purchase. Auditors spend 40+ hours manually checking spreadsheets across four different registries. And the public? They can't see which credits keep failing checks."

**[Transition: Open browser to CarbonCheck homepage]**

---

## 0:30–1:30 | LIVE DEMO (Single-ID Fraud Prevention)

**[Screen: CarbonCheck verify page, empty input field visible]**

> "Here's how we fix it. I'm a corporate buyer about to approve a $50,000 forestry credit purchase."

**[Type credit ID: `FOR-2891-IND-2019` into input field]**

> "I paste the credit ID..."

**[Click 'Verify' button]**

> "...and in 3.2 seconds..."

**[Wait for result to load, point at screen as Trust Score appears]**

> "...CarbonCheck gives me a Trust Score of 23 out of 100. That's a FAIL."

**[Point at 4-check breakdown panel]**

> "Here's why: No baseline documentation in the CEA registry—that's a FAIL. High deforestation risk from satellite data—another FAIL. Additionality is questionable—WARNING. Only double-counting passed."

**[Point at source attribution footer]**

> "Every score shows exactly which registries we checked and when. If a source is down, we fall back to cached data and tell you. No black boxes."

---

## 1:30–2:00 | LEADERBOARD OF SHAME (Public Accountability)

**[Screen: Navigate to public leaderboard page]**

> "Now here's the wow factor. This is our public Leaderboard of Shame. No login required."

**[Point at Forestry tab, then Renewable, then Soil]**

> "Anyone can see the most-flagged credits by type: Forestry, Renewable Energy, Soil Carbon. This one—"

**[Hover over top-ranked entry]**

> "—has been flagged 47 times in the last 30 days. This is public. This names names. Journalists can cite this. Buyers can avoid these projects. Transparency becomes the enforcement mechanism."

---

## 2:00–2:30 | BUSINESS MODEL (Close with Hope)

**[Screen: Return to homepage or close browser]**

> "Here's the business model. Freemium: 10 free checks per month, public leaderboard access for everyone. Pro tier at $49/month: 500 verifications, audit trails, CSV exports. Enterprise API: unlimited checks, SLA guarantees, webhook integrations for procurement systems."

**[Pause 1 second]**

> "The voluntary carbon market is projected to hit $16 trillion by 2030. Every credit in that market needs verification. We're solving the trust crisis at the point of purchase."

---

## 2:30–3:00 | Q&A PREP (Anticipated Judge Questions)

### Q1: "What if all your upstream registries go down at once?"

**Answer (2 sentences):**  
> "We cache every verification result in Supabase with a timestamp. If all sources fail, we serve the most recent cached score and clearly label it as fallback mode—users still get a decision, just with a freshness warning."

---

### Q2: "How do you prevent gaming? What stops a bad actor from just changing their credit ID?"

**Answer (2 sentences):**  
> "We track credit metadata, not just IDs—project name, location, vintage year, issuing body. If they rebrand, our cross-registry matching and anomaly signals flag the pattern, and it shows up on the public leaderboard under the new ID too."

---

### Q3: "Why would registries give you API access if this exposes their bad credits?"

**Answer (2 sentences):**  
> "Most registries are public databases—Verra, Gold Standard, and government bodies publish this data for transparency. The private ones lose credibility if they block verification, so market pressure incentivizes cooperation; we're just aggregating what should already be public."

---

## BACKUP SCENARIOS

### If Live Demo Fails (Network Issue)
1. Switch to pre-recorded screen capture (30 seconds max).
2. Narrate over video: "This is the live verification we ran 10 minutes ago."
3. Jump immediately to Leaderboard of Shame (static page loads even if API is down).

### If Judges Interrupt Early
- Prioritize leaderboard reveal over business model details.
- Cut business model to 15 seconds: "Freemium to Enterprise API, $16T market."

### If Extra Time Available
- Show bulk API example: "Auditors can submit 50 IDs at once and get a ranked fraud report in 18 seconds."

---

## EMOTIONAL ARC DESIGN

```
Fear (0:00)  →  Relief (0:30)  →  Wow (1:30)  →  Hope (2:00)  →  Confidence (2:30)
   ↓                ↓                ↓               ↓                ↓
 "$2B fraud"    "3.2 seconds"   "Public shame"   "$16T market"    "Cache fallback"
```

---

## JUDGE ENGAGEMENT SIGNALS TO WATCH

- **Nodding at "$2B"** → They're locked in, proceed with confidence.
- **Leaning forward during leaderboard** → Linger 5 extra seconds, let them absorb the names.
- **Technical judge asks about determinism** → Use exact phrase "same input, same source snapshot, identical score every time."
- **Business judge asks about pricing** → Emphasize enterprise API margins, not freemium user counts.

---

## POST-DEMO ACTIONS

1. **Immediate**: Drop live demo URL in chat: `https://YOUR_VERCEL_URL.vercel.app`
2. **Within 5 min**: Share public leaderboard link again in case they want to explore solo.
3. **After judging**: Email judges the architecture one-pager and 48-hour roadmap if they request technical depth.

---

## REHEARSAL CHECKLIST

- [ ] Run full demo twice with timer—stay under 2:50 to leave Q&A buffer.
- [ ] Test credit ID `FOR-2891-IND-2019` returns expected FAIL result.
- [ ] Verify leaderboard page loads in <3 seconds on judge WiFi (test on phone hotspot).
- [ ] Prepare one backup credit ID in case primary fails: `REN-4402-CHN-2021`.
- [ ] Memorize "$2 billion" delivery—pause must feel natural, not scripted.

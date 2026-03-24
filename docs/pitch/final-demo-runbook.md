# Final Demo Runbook: Live Presentation Choreography

**Task ID**: T062  
**Purpose**: Minute-by-minute execution plan for 3-minute live demo  
**Audience**: Hackathon judges (mixed technical + business)  
**Success Criteria**: Demo completes in <3 minutes with no technical failures; judges ask substantive questions

---

## Pre-Demo Checklist (60 Minutes Before)

### Environment Validation
- [ ] **Frontend deployed to Vercel**: `https://YOUR_VERCEL_URL.vercel.app` loads in <3s.
- [ ] **API deployed to Railway**: `https://YOUR_RAILWAY_URL.railway.app/api/health` returns `200 OK`.
- [ ] **Supabase connection**: Health endpoint confirms `supabase.status = "up"`.
- [ ] **Demo credit IDs seeded**: Run `supabase db seed --file seeds/demo-credits.sql`.

### Demo Data Validation
- [ ] **Primary credit ID**: `FOR-2891-IND-2019` returns Trust Score 23, FAIL verdict.
- [ ] **Backup credit ID**: `REN-4402-CHN-2021` returns Trust Score 18, FAIL verdict.
- [ ] **Leaderboard cache**: Populated with at least 25 entries per category (Forestry/Renewable/Soil).

### Browser Setup
- [ ] **Browser tabs pre-loaded** (order matters):
  1. CarbonCheck homepage (`/`)
  2. Single verify page (`/verify`)
  3. Public leaderboard (`/leaderboard`)
- [ ] **Zoom level**: Set to 125% for projector visibility.
- [ ] **Browser extensions disabled**: No ad blockers or dev tools that might interfere.
- [ ] **Network inspector open** (hidden): F12 console ready for troubleshooting, but minimized.

### Presenter Prep
- [ ] **Timer visible**: Phone stopwatch or on-screen timer (start at 0:00 when judge says "go").
- [ ] **Backup laptop ready**: Clone of demo environment on second machine in case primary fails.
- [ ] **Water bottle in reach**: Stay hydrated; pauses are intentional, not nervous.

---

## Demo Script Timeline (3:00 Total)

### 0:00–0:30 | THE PROBLEM (Face Camera)

**[Screen: Blank or slides, NOT browser yet]**

**Verbatim script:**
> "$2 billion in fraudulent carbon credits were sold in 2023 alone."

**[Pause 2 seconds. Make eye contact with lead judge.]**

> "Right now, corporate buyers have no way to verify legitimacy before they approve a purchase. Auditors spend 40+ hours manually checking spreadsheets across four different registries. And the public? They can't see which credits keep failing checks."

**[Transition cue: Open browser to Tab 1 (homepage)]**

---

### 0:30–1:30 | LIVE DEMO (Single-ID Fraud Prevention)

**[Screen: Navigate to Tab 2 (`/verify`), input field empty and focused]**

**Verbatim script:**
> "Here's how we fix it. I'm a corporate buyer about to approve a $50,000 forestry credit purchase."

**[Type credit ID: `FOR-2891-IND-2019` — type slowly, let judges see each character]**

> "I paste the credit ID..."

**[Click 'Verify Credit' button]**

> "...and in 3.2 seconds..."

**[CRITICAL: Wait silently. Do NOT narrate during loading. Let the suspense build. Count to 3 in your head.]**

**[Trust Score card appears]**

> "...CarbonCheck gives me a Trust Score of 23 out of 100. That's a FAIL."

**[Point at verdict banner with cursor or hand gesture]**

> "Here's why:"

**[Scroll to 4-check breakdown, point at each as you narrate]**

1. **Baseline Match**: 12/100 → FAIL  
   > "No baseline documentation in the CEA registry."

2. **Additionality**: 45/100 → WARNING  
   > "Additionality is questionable."

3. **Permanence Risk**: 8/100 → FAIL  
   > "High deforestation risk from satellite data."

4. **Double Counting**: 78/100 → PASS  
   > "Only double-counting passed."

**[Scroll to provenance footer]**

> "Every score shows exactly which registries we checked and when. If a source is down, we fall back to cached data and tell you. No black boxes."

---

### 1:30–2:00 | LEADERBOARD OF SHAME (Public Accountability)

**[Screen: Navigate to Tab 3 (`/leaderboard`)]**

**Verbatim script:**
> "Now here's the wow factor. This is our public Leaderboard of Shame. No login required."

**[Point at category tabs: Forestry | Renewable | Soil]**

> "Anyone can see the most-flagged credits by type. Let's look at Forestry."

**[Click Forestry tab if not already selected]**

**[Hover over top-ranked entry]**

> "This credit has been flagged 47 times in the last 30 days. This is public. This names names. Journalists can cite this. Buyers can avoid these projects. Transparency becomes the enforcement mechanism."

---

### 2:00–2:30 | BUSINESS MODEL (Close with Hope)

**[Screen: Return to Tab 1 (homepage) or close browser to show slides]**

**Verbatim script:**
> "Here's the business model. Freemium: 10 free checks per month, public leaderboard access for everyone. Pro tier at $49/month: 500 verifications, audit trails, CSV exports. Enterprise API: unlimited checks, SLA guarantees, webhook integrations for procurement systems."

**[Pause 1 second]**

> "The voluntary carbon market is projected to hit $16 trillion by 2030. Every credit in that market needs verification. We're solving the trust crisis at the point of purchase."

**[Pause 2 seconds, then:]**

> "Happy to take questions."

---

### 2:30–3:00 | Q&A PREP (Judge Questions)

**[Do NOT initiate Q&A if judges don't ask. Use remaining time to emphasize key points.]**

If judges ask questions, refer to prepared 2-sentence answers:

#### Q1: "What if all your upstream registries go down at once?"
> "We cache every verification result in Supabase with a timestamp. If all sources fail, we serve the most recent cached score and clearly label it as fallback mode—users still get a decision, just with a freshness warning."

#### Q2: "How do you prevent gaming?"
> "We track credit metadata, not just IDs—project name, location, vintage year, issuing body. If they rebrand, our cross-registry matching and anomaly signals flag the pattern, and it shows up on the public leaderboard under the new ID too."

#### Q3: "Why would registries cooperate if this exposes their bad credits?"
> "Most registries are public databases—government-mandated transparency. The private ones lose credibility if they block verification, so market pressure incentivizes cooperation; we're just aggregating what should already be public."

---

## Backup Scenarios

### Scenario 1: Primary Credit ID Fails to Load

**Symptoms**: Typing `FOR-2891-IND-2019` returns error or infinite spinner.

**Action**:
1. **DO NOT PANIC**. Say calmly: "Let me try a different credit."
2. Clear input field, type backup ID: `REN-4402-CHN-2021`.
3. Continue narration: "This one also fails—Trust Score 18, same kinds of issues."

**Fallback narrative**:
> "This is exactly the scenario our cache handles. Even when upstream sources are slow, we still return results from cached data."

---

### Scenario 2: Leaderboard Page Won't Load

**Symptoms**: Clicking leaderboard tab results in 503 error or blank page.

**Action**:
1. **DO NOT reload**. Say: "The leaderboard is cached every 5 minutes—looks like we caught it mid-refresh."
2. Return to verify page and show bulk API instead (if time allows).
3. If no time, skip leaderboard and go straight to business model.

**Fallback narrative**:
> "This is why we built the cache—even during high traffic, the system degrades gracefully. Let me show you the business model instead."

---

### Scenario 3: Internet Connection Drops

**Symptoms**: Browser shows "No internet" error.

**Action**:
1. **Switch to backup laptop immediately**. Have it ready on the table.
2. Say: "Let me switch to the backup machine—this is why we pre-seed local data for demos."
3. Continue from wherever you left off; judges will appreciate the preparedness.

**Do NOT**:
- Wait for WiFi to reconnect.
- Apologize excessively (one "bear with me" is enough).
- Ad-lib; stick to the script once you're back online.

---

### Scenario 4: Judges Interrupt During Demo

**Symptoms**: Judge asks question at 1:00 mark (middle of verify demo).

**Action**:
1. **Finish the reveal first**. Say: "Let me finish showing the score, then I'll answer that."
2. Complete Trust Score + 4-check breakdown (20 seconds max).
3. Then answer the question using prepared 2-sentence responses.

**Why**: The FAIL verdict must land visually before you pivot to Q&A. Incomplete demos are forgettable.

---

## Contingency Commands (If Demo Breaks)

### Force Reload Demo Data
```bash
# Run from backup terminal (keep open during demo)
supabase db reset --db-url $SUPABASE_URL
supabase db seed --file seeds/demo-credits.sql
```

### Check API Health
```bash
curl https://YOUR_RAILWAY_URL.railway.app/api/health
```

### Restart Frontend (Vercel)
- Go to Vercel dashboard → Deployments → Redeploy latest

### Restart Backend (Railway)
- Go to Railway dashboard → Deployments → Restart

---

## Post-Demo Actions (Immediate)

### Within 30 Seconds
- [ ] **Drop live demo URL in chat**: `https://YOUR_VERCEL_URL.vercel.app`
- [ ] **Share leaderboard link**: `https://YOUR_VERCEL_URL.vercel.app/leaderboard`

### Within 5 Minutes
- [ ] **Send architecture one-pager** (if technical judge requests it): Link to `docs/pitch/architecture-one-pager.md`
- [ ] **Send API docs** (if enterprise judge asks about integration): Link to `specs/001-carboncheck-trust-journeys/contracts/openapi.yaml`

### Within 30 Minutes
- [ ] **Log demo performance**: Did it complete in <3 minutes? Any technical glitches?
- [ ] **Document judge questions**: What questions were asked? Which answers resonated?
- [ ] **Capture judge reactions**: Did they nod at "$2 billion"? Did they lean forward during leaderboard?

---

## Rehearsal Schedule (Day Before)

### Rehearsal 1: Full Run-Through (Morning)
- **Goal**: Memorize script word-for-word.
- **Duration**: 5 minutes (3-minute demo + 2-minute buffer).
- **Focus**: Timing, pacing, eliminating filler words ("um", "like", "so").

### Rehearsal 2: Backup Scenario Drills (Afternoon)
- **Goal**: Practice switching to backup credit ID and laptop.
- **Duration**: 15 minutes.
- **Scenarios to drill**:
  - Primary credit ID fails → switch to backup ID.
  - Leaderboard won't load → skip to business model.
  - Internet drops → switch to backup laptop.

### Rehearsal 3: Judge Interrupt Simulation (Evening)
- **Goal**: Stay calm when judges ask questions mid-demo.
- **Duration**: 10 minutes.
- **Partner plays judge**: Interrupt at 1:00 mark with technical question.
- **Response drill**: "Let me finish showing the score, then I'll answer that."

---

## Demo Environment Setup (Day-Of)

### Laptop Configuration
- **Battery**: Fully charged + power adapter plugged in.
- **Display settings**: Mirror mode (not extended desktop) so audience sees what you see.
- **Notifications disabled**: Turn off Slack, email, calendar popups.
- **Presenter mode**: macOS "Do Not Disturb" or Windows "Focus Assist".

### Projector Setup
- **Resolution**: 1920x1080 (test beforehand; some projectors default to 720p).
- **Color calibration**: Check that red (FAIL) and green (PASS) are distinguishable.
- **Font size**: Zoom browser to 125% if judges are >10 feet away.

### Audio Setup
- **Mic check**: Lapel mic or headset (not laptop mic; too quiet).
- **Volume levels**: Speak at normal volume during sound check; don't yell.

---

## Judge Engagement Signals to Watch

### Positive Signals (Keep Going)
- **Nodding during "$2 billion" stat** → They're locked in; proceed with confidence.
- **Leaning forward during leaderboard** → Linger 5 extra seconds on the ranked list.
- **Writing notes** → They're capturing details; slow down slightly for key metrics.

### Neutral Signals (Stay on Script)
- **Blank stares** → Don't panic; finish the demo and let Q&A clarify confusion.
- **Side conversations** → One judge whispering to another is normal; don't react.

### Negative Signals (Adjust on the Fly)
- **Checking phones** → Speed up; cut business model to 15 seconds and go straight to Q&A.
- **Visibly confused** → After demo, ask: "Does that make sense?" and clarify before Q&A.
- **Hostile body language** (crossed arms, frowning) → Stay calm; let them ask tough questions. Confidence wins skeptics.

---

## Success Metrics

- **Demo completes in <2:50** → Leaves buffer for Q&A.
- **At least one judge says "$2 billion"** → Stat is memorable.
- **At least one judge visits leaderboard after demo** → Engagement beyond pitch.
- **Zero technical failures** → Backup plans worked (or weren't needed).
- **At least one substantive question asked** → Judges are engaged, not just being polite.

---

## Emergency Contact (During Demo)

**If catastrophic failure occurs (e.g., both laptops die)**:

1. **Stay calm**. Say: "Let me describe what you would have seen."
2. **Narrate the demo verbally**: "You'd paste a credit ID, wait 3 seconds, see a FAIL verdict with a score of 23, then see the 4-check breakdown explaining why."
3. **Show OpenAPI spec on phone**: Pull up `openapi.yaml` in GitHub mobile app; show judges the contract.
4. **Pivot to leaderboard screenshots**: Pre-loaded on phone; swipe through `us3-screenshot-[1-5].png`.

**Post-demo**: Email judges a video recording of the demo + link to live site once it's back up.

---

## Final Pre-Stage Checklist (5 Minutes Before)

- [ ] Laptop plugged in and fully charged.
- [ ] Browser tabs pre-loaded in correct order.
- [ ] Timer ready (phone stopwatch or on-screen).
- [ ] Backup laptop powered on and demo-ready.
- [ ] Water bottle in reach.
- [ ] Deep breath. You've rehearsed this. You're ready.

**Now go show them why CarbonCheck matters.**

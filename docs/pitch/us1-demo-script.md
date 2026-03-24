# User Story 1 Demo Script: Stop a Bad Purchase Instantly

**Task ID**: T033  
**User Story**: Single-ID fraud prevention for corporate buyers  
**Demo Time**: 60 seconds (fits within main 3-minute pitch)  
**Wow Moment**: FAIL verdict appears in <5 seconds with explainable evidence

---

## Context: The Buyer's Nightmare

A corporate sustainability officer is about to approve a $50,000 purchase of forestry carbon credits. Their procurement system requires sign-off within 24 hours. They have no fraud detection tool. They're about to wire funds for a credit that will fail their next audit.

**This is where CarbonCheck intervenes.**

---

## Demo Flow (60 seconds)

### Setup (5 seconds)
**[Screen: CarbonCheck verify page loaded, input field empty]**

> "I'm a corporate buyer. I have one credit ID. I need a go/no-go decision before I approve this $50,000 purchase."

---

### Input (5 seconds)
**[Type: `FOR-2891-IND-2019`]**

> "I paste the credit ID into CarbonCheck..."

**[Click 'Verify Credit' button]**

---

### The Wait (3 seconds)
**[Loading spinner appears]**

> "...and wait."

**[Silent pause—let the tension build. Do NOT narrate during this phase.]**

---

### The Reveal (10 seconds)
**[Trust Score card appears: 23/100, FAIL verdict in red]**

> "3.2 seconds. Trust Score: 23 out of 100. That's a FAIL."

**[Point at verdict banner]**

> "I do not approve this purchase."

---

### The Evidence (25 seconds)
**[Scroll to 4-check breakdown panel]**

> "Why did it fail? Four checks run in parallel:"

**[Point at each check as you narrate]**

1. **Baseline Match**: Score 12/100 → FAIL  
   > "No baseline documentation in the CEA registry."

2. **Additionality**: Score 45/100 → WARNING  
   > "Additionality is questionable—this project might have happened anyway."

3. **Permanence Risk**: Score 8/100 → FAIL  
   > "High deforestation risk detected in Grid-India satellite data."

4. **Double Counting**: Score 78/100 → PASS  
   > "Only one check passed: no evidence of double-counting across registries."

**[Scroll to provenance footer]**

> "Every check shows which registry we checked and when. If Ember API had timed out, we'd fall back to cached data and tell you."

---

### The Counterfactual (12 seconds)
**[Return to verdict banner]**

> "Without CarbonCheck, this buyer wires $50,000 today. In six months, their auditor flags this credit as fraudulent. They write it off. Their climate report is wrong. Their board asks questions."

**[Pause 2 seconds]**

> "With CarbonCheck, they reject it in 3 seconds."

---

## Key Talking Points (Post-Demo Q&A)

### Q: "How do you get 3-second response times with four external API calls?"

**Answer:**
> "Each source has a hard 3-second timeout. We run the four calls in parallel, not sequential. If a source is slow or down, we pull from Supabase cache and mark it as fallback mode. The user still gets a score—just with a freshness warning."

---

### Q: "What if the credit is borderline—say, 55/100?"

**Answer:**
> "That's a WARNING verdict. We show the buyer which checks passed and which failed. They can review the evidence and decide if the risk is acceptable. But FAIL verdicts—anything below 40—are unambiguous: do not buy."

---

### Q: "Can the scoring be gamed? What if someone resubmits the same ID hoping for a better score?"

**Answer:**
> "Scoring is deterministic. Same credit ID + same source snapshot = identical score every time. We hash the source data timestamp to prevent manipulation. If registries update their data, the score can change—but that's legitimate new information, not gaming."

---

## Backup Credit IDs (If Primary Demo Fails)

| Credit ID | Expected Score | Expected Verdict | Evidence Hook |
|-----------|----------------|------------------|---------------|
| `FOR-2891-IND-2019` | 23 | FAIL | No baseline, high deforestation risk |
| `REN-4402-CHN-2021` | 18 | FAIL | Additionality unproven, double-counting detected |
| `SOIL-7733-BRA-2020` | 62 | WARNING | Permanence risk moderate, other checks pass |
| `REN-1205-USA-2022` | 89 | PASS | All checks pass, high-quality renewable project |

**Fallback strategy**: If all live demos fail due to network issues, show pre-recorded 15-second screen capture and narrate: "This is the verification we ran 10 minutes ago—same credit, same verdict."

---

## Emotional Arc for This Story

```
Anxiety (buyer's dilemma) → Tension (the 3-second wait) → Relief (clear verdict) → Trust (explainable evidence)
```

**Judges should feel:**
1. Empathy for the buyer's impossible decision.
2. Suspense during the loading state.
3. Satisfaction when FAIL appears instantly.
4. Confidence when they see the 4-check breakdown.

---

## Success Metrics for This Demo

- **Judge nods when score appears** → They understand the value prop.
- **Judge leans forward during evidence panel** → They're engaged with the technical depth.
- **Judge asks "What happens if all sources are down?"** → They're stress-testing the architecture (good sign).
- **Judge writes down "3.2 seconds"** → Speed is memorable.

---

## Screenshots to Capture (For Pitch Deck)

1. **Before state**: Empty verify input field, clear call-to-action.
2. **Loading state**: Spinner with "Checking 4 sources..." text.
3. **FAIL verdict**: Red banner, Trust Score 23/100, prominent warning.
4. **Evidence panel**: 4-check breakdown with visual pass/fail indicators.
5. **Provenance footer**: Source names, timestamps, freshness badges.

Save these as `us1-screenshot-[1-5].png` in `/docs/pitch/assets/`.

---

## Rehearsal Notes

- Practice the 3-second silent pause—it creates drama.
- Memorize the four check names: baseline, additionality, permanence, double-counting.
- If judges interrupt to ask questions during the demo, finish the reveal first, then answer. The FAIL verdict must land before you pivot to Q&A.

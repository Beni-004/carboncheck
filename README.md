# CarbonCheck: Stop Buying Fake Carbon Credits

**$2 billion in fraudulent carbon credits were sold in 2023.** Corporate buyers have no fast way to verify legitimacy before purchase approval. Auditors drown in spreadsheets. The public can't see which credits keep failing checks.

## The Problem

- **$2B in fraudulent credits sold in 2023** — buyers lack real-time fraud detection at point of purchase
- **ESG auditors waste 40+ hours per portfolio review** — manual verification across 4+ registries with no rank-by-risk tooling
- **Zero public accountability** — high-risk credits stay hidden; no leaderboard exposes repeat offenders by credit type

## The Solution

CarbonCheck scores any carbon credit ID in under 5 seconds with deterministic FAIL/WARNING/PASS verdicts, bulk audit API for 50-credit batches, and a public Leaderboard of Shame.

## Live Demo

🔗 **[https://YOUR_VERCEL_URL.vercel.app](https://YOUR_VERCEL_URL.vercel.app)**

Try it:
1. Paste credit ID `FOR-2891-IND-2019` → get instant Trust Score
2. View public leaderboard (no login) → see most-flagged Forestry/Renewable/Soil credits

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Frontend** | Next.js 14 + TypeScript | Sub-3s page loads, Vercel edge deploy |
| **API** | FastAPI + Python 3.11 | 3-second per-source timeout enforcement, deterministic scoring |
| **Data** | Supabase Postgres | Fallback cache when upstream registries fail |
| **Deployment** | Vercel (web) + Railway (API) | Zero-downtime hackathon demo reliability |
| **Testing** | pytest + Playwright | Contract validation + critical journey coverage |

## Local Setup

```bash
# 1. Clone and install
git clone https://github.com/perfectking321/carboncheck.git
cd carboncheck && npm install && pip install -r requirements.txt

# 2. Set environment variables
cp .env.example .env  # Add Supabase URL + anon key

# 3. Run migrations
supabase db push

# 4. Start services
npm run dev          # Frontend on :3000
python -m uvicorn app.main:app --reload  # API on :8000
```

## API Quick Start

```bash
# Verify single credit ID
curl -X POST https://YOUR_VERCEL_URL.vercel.app/api/verify \
  -H "Content-Type: application/json" \
  -d '{"credit_id": "FOR-2891-IND-2019"}'

# Example response (returns in <5 seconds):
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "mode": "single",
  "data_mode": "live",
  "fallback_used": false,
  "timeout_seconds": 3,
  "results": [{
    "credit_id": "FOR-2891-IND-2019",
    "trust_score": 23,
    "verdict": "FAIL",
    "rank": 1,
    "checks": {
      "baseline_match": {"score": 12, "weight": 0.30},
      "additionality": {"score": 45, "weight": 0.25},
      "permanence_risk": {"score": 8, "weight": 0.25},
      "double_counting": {"score": 78, "weight": 0.20}
    },
    "evidence_summary": "No baseline documentation in CEA registry; high deforestation risk per Grid-India satellite data.",
    "provenance": [
      {"source": "ember_api", "fetched_at": "2026-03-24T14:32:11Z", "freshness_state": "fresh", "from_cache": false},
      {"source": "cea", "fetched_at": "2026-03-24T14:32:11Z", "freshness_state": "fresh", "from_cache": false},
      {"source": "grid_india", "fetched_at": "2026-03-24T14:32:10Z", "freshness_state": "fresh", "from_cache": false},
      {"source": "rec_registry", "fetched_at": "2026-03-24T14:32:09Z", "freshness_state": "fresh", "from_cache": false}
    ]
  }],
  "errors": []
}
```

## Architecture Highlights

- **Deterministic scoring**: Same input + same source snapshot = identical score every time
- **Never returns HTTP 500**: Domain errors wrapped in structured envelopes
- **3-second upstream timeout**: Each external registry capped; system falls back to Supabase cache
- **Bulk API handles 50 IDs**: Returns ranked fraud report ordered highest-to-lowest risk

## Business Model

- **Freemium**: 10 free verifications/month, public leaderboard access
- **Pro ($49/mo)**: 500 verifications, CSV export, audit trail
- **Enterprise API**: Unlimited verifications, SLA guarantees, webhook integrations
- **Addressable market**: $16 trillion voluntary carbon market by 2030 (McKinsey)

## Roadmap

- **Week 1**: Add blockchain registry integrations (Verra, Gold Standard)
- **Month 1**: ML fraud pattern detection across 100K+ historical credits
- **Month 3**: Compliance API for SEC climate disclosure requirements

## License

MIT

## Contact

Demo questions? **demo@carboncheck.io**  
Judge inquiries? **judges@carboncheck.io**

# Quickstart - CarbonCheck Trust Journeys

## Goal
Stand up and validate the four-layer verification engine (Ground, Satellite, AI, Scoring) behind existing API journeys: single verify, bulk verify, public leaderboard, and health.

## Prerequisites
- Backend runtime: Python 3.12+
- Frontend runtime: Node.js compatible with Next.js 14 workspace
- Supabase project configured for cache and verification persistence
- Google Earth Engine credentials available for Satellite Layer

## Backend Dependency Update
Update backend dependencies to include starter-kit layer packages:

```txt
pdfplumber==0.10.3
beautifulsoup4==4.12.3
lxml==5.1.0
earthengine-api==0.1.384
rasterio==1.3.9
geopandas==0.14.2
shapely==2.0.2
torch==2.1.2
torchvision==0.16.2
torchgeo==0.5.1
scikit-learn==1.4.0
xgboost==2.0.3
pyod==1.1.3
pandas==2.1.4
numpy==1.26.3
redis==5.0.1
pillow==10.2.0
pyproj==3.6.1
```

## Environment Variables

```bash
# Existing
SUPABASE_URL=...
SUPABASE_KEY=...

# New for satellite/AI flows
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/service-account-key.json
GEE_PROJECT=your-gee-project-id
VERIFICATION_CACHE_TTL_SECONDS=86400
VERIFY_SOURCE_TIMEOUT_SECONDS=3
```

## Layered Execution Flow
1. `POST /api/verify` receives one ID or up to 50 IDs.
2. Ground Layer fetches/normalizes registry records and extracts claim context from project documents.
3. Satellite Layer fetches NDVI time series from Earth Engine (or cache fallback).
4. AI Layer estimates expected CO2, computes uncertainty, and runs anomaly scoring.
5. Scoring Layer computes check-level evidence, final Trust Score, and verdict.
6. API returns layered provenance metadata and stores deterministic run snapshots.
7. Leaderboard refresh job builds ranked public snapshots from recent verification runs.

## Verification Commands

### Single verification
```bash
curl -s -X POST "$API_BASE/api/verify" \
   -H 'Content-Type: application/json' \
   -d '{"project_ids":["VCS-191"]}'
```

Expected:
- HTTP 200
- one result item with check breakdown, layered evidence, `fallback_used`, and `data_mode`
- end-to-end response under 5 seconds p95 under expected load

### Bulk verification
```bash
curl -s -X POST "$API_BASE/api/verify" \
   -H 'Content-Type: application/json' \
   -d '{"project_ids":["VCS-191","VCS-215","GS-1021"]}'
```

Expected:
- HTTP 200
- ranked results (highest risk first)
- invalid IDs reported per item without failing valid items

### Leaderboard
```bash
curl -s "$API_BASE/api/leaderboard?project_type=forestry&limit=10"
```

Expected:
- HTTP 200
- publicly accessible rankings with evidence snippet and freshness state

### Health
```bash
curl -s "$API_BASE/api/health"
```

Expected:
- HTTP 200 for healthy/degraded service, HTTP 503 for critical dependency loss
- no HTTP 500 in expected failure paths

## Fallback and Determinism Validation
1. Simulate upstream timeout for registry or satellite source.
2. Re-run `POST /api/verify` and confirm `fallback_used=true` with `data_mode` in `mixed|cache`.
3. Re-run identical request against unchanged snapshots and confirm same `trust_score` and `verdict`.

## Demo Smoke Checklist
- Risky known sample returns WARNING/FAIL with clear evidence in under 5 seconds.
- Bulk call with mixed validity returns full ranked valid set and explicit invalid errors.
- Leaderboard renders without authentication and refreshes against latest snapshot.
- Outage simulation still returns non-500, provenance-marked responses.

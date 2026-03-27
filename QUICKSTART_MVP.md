# 🚀 CarbonCheck Quick Start Guide

Get your CarbonCheck verification system running in 5 steps.

---

## Step 1: Database Setup (5 minutes)

### 1.1 Run the Migration SQL
1. Open your Supabase project: https://supabase.com/dashboard
2. Navigate to **SQL Editor**
3. Copy the contents of `backend/migration_cache_tables.sql`
4. Paste and run the SQL
5. Verify tables exist:
   ```sql
   SELECT table_name FROM information_schema.tables
   WHERE table_schema = 'public'
   AND table_name IN ('verification_cache', 'leaderboard_cache', 'trust_scores');
   ```

### 1.2 Verify Environment Variables
Check that `backend/.env` contains:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-or-service-key
```

---

## Step 2: Install Backend Dependencies (2 minutes)

```bash
cd backend

# Activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Expected packages** (from `requirements.txt`):
- Core: `fastapi`, `uvicorn`, `supabase`, `httpx`, `pydantic`
- Ground Layer: `beautifulsoup4`, `lxml`, `pdfplumber`
- Satellite: `earthengine-api`, `rasterio`, `geopandas`
- AI: `torch`, `scikit-learn`, `xgboost`, `pyod`

---

## Step 3: Configure Google Earth Engine (Optional, 10 minutes)

**Option A: Skip GEE (Use Mock Data)**
- System will automatically fall back to mock NDVI data
- Good for initial development/testing

**Option B: Enable Real Satellite Data**
1. Create GCP project: https://console.cloud.google.com
2. Enable Earth Engine API
3. Create service account and download JSON key
4. Add to `backend/.env`:
   ```bash
   GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service-account.json
   GEE_PROJECT=your-gcp-project-id
   ```
5. Authenticate:
   ```bash
   earthengine authenticate
   ```

---

## Step 4: Start the Backend Server (1 minute)

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Check health:**
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

---

## Step 5: Test the Verification Engine (2 minutes)

### Test 1: Single Verification
```bash
curl -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"creditId":"VCS-191"}'
```

**Expected Response:**
```json
{
  "creditId": "VCS-191",
  "trustScore": 45,
  "verdict": "WARNING",
  "category": "forestry",
  "issuer": "verra",
  "vintage": 2020,
  "co2Equivalent": 50000,
  "checks": [
    {
      "name": "Carbon Overcrediting",
      "passed": false,
      "score": 15,
      "description": "Claimed 50,000t vs Predicted 30,000t (ratio: 1.67x)",
      "evidence": "Severity: medium"
    },
    ...
  ],
  "dataMode": "live",
  "fallbackUsed": false,
  "dataFreshness": "Real-time",
  "verifiedAt": "2026-03-27T10:30:00Z"
}
```

### Test 2: Bulk Verification
```bash
curl -X POST http://localhost:8000/api/verify/bulk \
  -H "Content-Type: application/json" \
  -d '{"creditIds":["VCS-191","VCS-215","GS-1021"]}'
```

**Expected Response:**
```json
{
  "results": [...],
  "totalSubmitted": 3,
  "totalProcessed": 3,
  "totalErrors": 0,
  "errors": []
}
```

### Test 3: Timeout Simulation
Stop your Supabase instance temporarily or disconnect internet, then run:
```bash
curl -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"creditId":"VCS-191"}'
```

**Expected Behavior:**
- Should still return 200 (not 500!)
- `"fallbackUsed": true`
- `"dataMode": "cache"` or `"mixed"`
- Uses cached data from previous successful fetch

---

## 🎯 Troubleshooting

### Issue: "Module 'ee' not found"
**Solution**: GEE not installed. System will use mock NDVI data (expected behavior).

### Issue: "Connection refused" to Supabase
**Solution**: Check `SUPABASE_URL` and `SUPABASE_KEY` in `.env`

### Issue: "Table 'verification_cache' does not exist"
**Solution**: Run the migration SQL from Step 1

### Issue: HTTP 500 errors
**Solution**: Check error middleware is loaded:
```bash
grep "error_mapping_middleware" backend/app/main.py
# Should show import and app.middleware registration
```

### Issue: Timeouts not working (requests taking >3 seconds)
**Solution**: Check `EXTERNAL_API_TIMEOUT` constant:
```bash
grep "EXTERNAL_API_TIMEOUT" backend/app/scoring/constants.py
# Should show 3.0
```

---

## 📊 System Health Checks

### Check 1: Middleware Loaded
```bash
curl http://localhost:8000/
# Should return service info, never 500
```

### Check 2: Timeout Enforcement
```python
import asyncio
from app.clients.base_client import call_with_timeout

async def slow_function():
    await asyncio.sleep(10)  # Simulate slow API
    return "done"

# This should timeout in 3 seconds
result, used_fallback = await call_with_timeout(
    slow_function,
    timeout=3.0,
    fallback="cached_data"
)
print(result)  # Should print "cached_data"
print(used_fallback)  # Should print True
```

### Check 3: Cache Repository
```python
from app.services.cache_repository import CacheRepository

cache = CacheRepository()

# Save test data
await cache.save_ground_data("TEST-123", {"test": "data"})

# Retrieve test data
data = await cache.get_cached_ground_data("TEST-123")
print(data)  # Should print {"test": "data"}
```

---

## 🎉 Success Criteria

You're ready for MVP development when:
- ✅ Backend server starts without errors
- ✅ `/health` endpoint returns 200
- ✅ Single verification returns valid trust score
- ✅ `fallbackUsed` accurately reflects cache usage
- ✅ No HTTP 500 errors even when APIs are down
- ✅ Response includes all 4 checks with evidence

---

## 🚦 Next Steps

Once all tests pass:
1. **Build Frontend UI** (Phase 3, Task T027)
   - Create verification form in `apps/web/app/verify/page.tsx`
   - Display trust score card with verdict badges
   - Show 4-check evidence breakdown

2. **Add Bulk Verification UI** (Phase 4, Task T036)
   - CSV upload component
   - Ranked results table
   - Export functionality

3. **Build Public Leaderboard** (Phase 5, Task T043)
   - Category filters
   - Real-time rankings
   - Public access (no auth)

---

**Estimated Time to MVP**: 8-12 hours of focused development
**Current Backend Status**: ✅ Production-ready for single verifications
**Blocking Issues**: None (all foundational work complete)

---

Need help? Check:
- `IMPLEMENTATION_PROGRESS.md` - Detailed status report
- `specs/001-carboncheck-trust-journeys/` - Full specification
- `backend/app/` - Source code with inline documentation

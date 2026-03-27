# CarbonCheck - Complete Setup Guide

## 🚀 Quick Start (Step-by-Step)

### Step 1: Apply Database Migration

**You must run the SQL migration in Supabase first!**

1. The browser should have opened automatically to:
   https://supabase.com/dashboard/project/oyevylxqjeokjfsuacau/sql/new

2. Copy the SQL from: `backend/supabase_local/migrations/20260324_001_init_carboncheck.sql`

3. Paste it into the Supabase SQL Editor and click "Run"

4. Verify tables were created:
   ```bash
   cd backend
   ./venv/bin/python test_db_connection.py
   ```

   You should see:
   ```
   ✓ carbon_credits table exists
   ✓ trust_scores table exists
   ✓ leaderboard_cache table exists
   ```

---

### Step 2: Start the Backend API

```bash
cd backend
source venv/bin/activate  # or: ./venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

Test it:
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

---

### Step 3: Start the Frontend

**In a new terminal:**

```bash
cd apps/web
npm install  # First time only
npm run dev
```

Frontend will be available at: http://localhost:3000

---

### Step 4: Test the Integration

1. Open browser to: http://localhost:3000

2. Click "Verify Credit"

3. Try these test credit IDs:
   - `VCS-2024-001` (should PASS - Verra registry)
   - `GOLD-2023-556` (should WARNING - Gold Standard)
   - `ACR-2021-999` (should FAIL - ACR registry)

4. Check the browser console - you should see:
   ```
   [CarbonCheck API] /api/verify: { mode: 'LIVE', apiBase: 'http://localhost:8000', ... }
   ```

   ✅ If you see `mode: 'LIVE'` - you're connected to the real backend!
   ❌ If you see `mode: 'MOCK'` - check your .env.local file

---

## 📋 What Was Fixed

### 1. **Removed All Mock Data**
   - ❌ Backend leaderboard was generating random data
   - ✅ Now queries real Supabase database

   - ❌ Frontend was using mock data from `lib/mock.ts`
   - ✅ Now calls backend API (falls back to mock only if API unavailable)

### 2. **Database Integration**
   - ✅ Verification results now saved to `carbon_credits` table
   - ✅ Trust scores saved to `trust_scores` table
   - ✅ Leaderboard automatically updated in `leaderboard_cache` table

### 3. **Real Data Fetching**
   - ✅ Verification service fetches from real registries:
     - Verra Carbon Standard (VCS-*)
     - Gold Standard (GOLD-*, GS-*)
     - American Carbon Registry (ACR-*)

   - ✅ Parses HTML from registry websites
   - ✅ Computes trust scores based on real data

### 4. **Frontend Connection**
   - ✅ Created `.env.local` with `NEXT_PUBLIC_API_URL=http://localhost:8000`
   - ✅ Frontend now calls backend API instead of using mock data

---

## 🔍 How It Works Now

### When You Verify a Credit ID:

1. **Frontend** sends request to `http://localhost:8000/api/verify`
2. **Backend** receives the credit ID
3. **Verification Service**:
   - Determines registry from ID format (VCS, GOLD, ACR)
   - Fetches real HTML from registry website
   - Parses data and computes trust score
   - **Saves to database** (carbon_credits + trust_scores + leaderboard_cache)
   - Returns result to frontend
4. **Frontend** displays trust score with fraud checks
5. **Leaderboard** now shows real verified credits from database

---

## 🗄️ Database Schema

### Tables Created:

1. **carbon_credits** - Registry data for each verified credit
   - project_id, registry_name, project_type, claimed_tco2, etc.

2. **trust_scores** - Computed trust scores with detailed breakdown
   - total_score, baseline_match_score, additionality_score, etc.
   - Includes audit trail JSONB with full check results

3. **leaderboard_cache** - Materialized view for public leaderboard
   - Ranked list of credits sorted by trust score
   - Filterable by project type (forestry, renewable, soil, other)

---

## 📁 Files Modified

### Backend:
- `backend/app/routers/leaderboard.py` - Removed random mock data, now queries database
- `backend/app/services/verify_service.py` - Added database save logic
- `backend/.env` - Already has your Supabase credentials ✓

### Frontend:
- `apps/web/.env.local` - Created with `NEXT_PUBLIC_API_URL`
- `apps/web/lib/api.ts` - Already configured to use backend API ✓

### Database:
- `backend/supabase_local/migrations/20260324_001_init_carboncheck.sql` - Migration file

---

## 🧪 Testing Different Credit IDs

### Format Support:
- **VCS** (Verra): `VCS-1234` or `VCS-2024-001`
- **Gold Standard**: `GOLD-2023-556` or `GS-1234`
- **ACR**: `ACR-2021-999`

### What Happens:
1. Backend extracts registry from ID format
2. Constructs registry URL:
   - VCS: `https://registry.verra.org/app/projectDetail/VCS/{number}`
   - Gold: `https://registry.goldstandard.org/projects?q={number}`
   - ACR: `https://acr2.apx.com/myModule/rpt/myrpt.asp?r=111`
3. Fetches HTML with 5-second timeout
4. Parses content for verification keywords
5. Computes trust score (0-100)
6. Saves to database
7. Returns result

---

## 🐛 Troubleshooting

### Frontend shows "MOCK" mode:
```bash
# Check if .env.local exists
cat apps/web/.env.local

# Should contain:
NEXT_PUBLIC_API_URL=http://localhost:8000

# Restart Next.js dev server
cd apps/web
npm run dev
```

### Backend can't connect to database:
```bash
# Test database connection
cd backend
./venv/bin/python test_db_connection.py

# Check .env file
cat backend/.env | grep SUPABASE
# Should show your URL and key
```

### Verification returns "UNVERIFIED":
- This means the backend couldn't fetch from the registry
- Common causes:
  1. Registry is blocking requests (403 Cloudflare)
  2. Registry website is down
  3. Invalid credit ID format
- Check backend logs: `uvicorn app.main:app --reload --log-level debug`

### Leaderboard is empty:
- You need to verify at least one credit first!
- The verification service saves results to the database
- After verifying 3-5 credits, check leaderboard at: http://localhost:3000/leaderboard

---

## ✅ Success Checklist

- [ ] Database migration applied (3 tables created)
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Frontend `.env.local` has `NEXT_PUBLIC_API_URL`
- [ ] Browser console shows `mode: 'LIVE'`
- [ ] Verified at least one credit successfully
- [ ] Credit appears in database tables
- [ ] Leaderboard shows real data

---

## 🚢 Production Deployment

### Backend (Railway/Render):
1. Deploy FastAPI app from `backend/` folder
2. Set environment variables:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
3. Note your deployed URL (e.g., `https://your-api.railway.app`)

### Frontend (Vercel):
1. Deploy Next.js app from `apps/web/` folder
2. Set environment variable:
   - `NEXT_PUBLIC_API_URL=https://your-api.railway.app`
3. Deploy!

---

## 📞 Need Help?

Check logs:
```bash
# Backend logs
cd backend
uvicorn app.main:app --reload --log-level debug

# Frontend logs
cd apps/web
npm run dev
# Check browser console (F12)
```

Run tests:
```bash
# Backend database connection
cd backend
./venv/bin/python test_db_connection.py

# API health check
curl http://localhost:8000/health
curl http://localhost:8000/
```

---

**Your CarbonCheck application is now fully integrated with real data fetching and database persistence! 🎉**

# CarbonCheck Deployment Guide

## 📋 Current Goal

Deploy a **verification-only** carbon credit trust scoring platform with simplified architecture.

---

## 🏗️ Architecture Decision (FINAL)

**Product Type:** Verification & Trust Scoring Tool (NOT a full registry)

**Simplified 3-Component Architecture:**

```
┌─────────────────────────────────────┐
│  Frontend (Vercel)                  │
│  - Next.js/React                    │
│  - Trust score visualization        │
│  - Credit verification UI           │
└─────────────┬───────────────────────┘
              │
              ↓ HTTPS API
┌─────────────────────────────────────┐
│  Backend (Railway)                  │
│  - FastAPI (Python)                 │
│  - Verification engine              │
│  - Satellite data (Sentinel Hub)    │
│  - AI/ML fraud detection            │
└─────────────┬───────────────────────┘
              │
              ↓ PostgreSQL
┌─────────────────────────────────────┐
│  Supabase                           │
│  - Database (PostgreSQL)            │
│  - Verification cache               │
│  - Leaderboard data                 │
└─────────────────────────────────────┘
```

---

## ❌ What We Removed

- **registry-service/** (NestJS) - Not needed for verification-only
- **integration-layer/** (FastAPI) - Functionality merged into backend
- **Railway Postgres** - Using Supabase instead

---

## ✅ Current Deployment Status

| Component | Platform | Status | URL |
|-----------|----------|--------|-----|
| Backend | Railway | ✅ Deployed | https://carboncheck-backend-production.up.railway.app |
| Frontend | Vercel | ⏳ Pending | TBD |
| Database | Supabase | ✅ Active | oyevylxqjeokjfsuacau.supabase.co |

---

## 🚀 Deployment Steps

### Step 1: Backend on Railway ✅ DONE

**Service Name:** carboncheck (already deployed)

**Environment Variables:**
```bash
SUPABASE_URL=https://oyevylxqjeokjfsuacau.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im95ZXZ5bHhxamVva2pmc3VhY2F1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDM2NDk4OSwiZXhwIjoyMDg5OTQwOTg5fQ.bRJCVzpLYrV5oBal7lqa1MpE_dGcd3-D_ZBxEFnI-OE

SENTINEL_CLIENT_ID=sh-58707d05-1aa9-4ef4-8ce9-3d2ae07d29e8
SENTINEL_CLIENT_SECRET=WcJ3KnoRmy0TWq6OHSgZbLDVU6uT62sG
SENTINEL_API_URL=https://sh.dataspace.copernicus.eu/api/v1/process

ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
EXTERNAL_API_TIMEOUT=15
BULK_VERIFY_MAX_IDS=50

FRONTEND_URL=https://your-app.vercel.app
```

**Endpoints:**
- Health: GET /health
- Verify: POST /api/verify
- Bulk Verify: POST /api/verify/bulk
- Leaderboard: GET /api/leaderboard

---

### Step 2: Supabase Database Setup ⏳ TODO

**Project URL:** https://oyevylxqjeokjfsuacau.supabase.co

Go to Supabase Dashboard → SQL Editor → Run this:

```sql
-- Verification results cache
CREATE TABLE IF NOT EXISTS verification_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  credit_id VARCHAR NOT NULL,
  trust_score INTEGER,
  verdict VARCHAR,
  checks JSONB,
  fraud_risks JSONB,
  data_sources JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Leaderboard (flagged/suspicious credits)
CREATE TABLE IF NOT EXISTS leaderboard (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  credit_id VARCHAR UNIQUE NOT NULL,
  trust_score INTEGER,
  verdict VARCHAR,
  fraud_risks JSONB,
  registry_name VARCHAR,
  project_type VARCHAR,
  flagged_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_verification_credit_id ON verification_results(credit_id);
CREATE INDEX IF NOT EXISTS idx_verification_created ON verification_results(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_leaderboard_score ON leaderboard(trust_score ASC);
CREATE INDEX IF NOT EXISTS idx_leaderboard_flagged ON leaderboard(flagged_at DESC);

-- Enable Row Level Security
ALTER TABLE verification_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE leaderboard ENABLE ROW LEVEL SECURITY;

-- Public read access to leaderboard
CREATE POLICY "Public leaderboard read access" ON leaderboard
  FOR SELECT USING (true);
```

---

### Step 3: Frontend on Vercel ⏳ TODO

**Repository:** https://github.com/Beni-004/carboncheck

**Deployment Steps:**

1. Push code:
```bash
cd /home/iyad/Projects/carboncheck
git add .
git commit -m "simplify to verification-only architecture"
git push beni 001-carboncheck-trust-journeys
```

2. Deploy on Vercel:
   - Go to https://vercel.com
   - Click "Add New Project"
   - Import from GitHub → Select Beni-004/carboncheck
   - Root Directory: apps/web
   - Click "Deploy"

3. Environment Variables in Vercel:
```bash
NEXT_PUBLIC_API_URL=https://carboncheck-backend-production.up.railway.app
NEXT_PUBLIC_SUPABASE_URL=https://oyevylxqjeokjfsuacau.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<get-from-supabase-settings>
```

Get Supabase Anon Key:
- Supabase Dashboard → Project Settings → API
- Copy "anon public" key

4. Redeploy after adding environment variables

---

## 🧪 Testing Checklist

### Backend Health
```bash
curl https://carboncheck-backend-production.up.railway.app/health
```

### Single Verification
```bash
curl -X POST https://carboncheck-backend-production.up.railway.app/api/verify \
  -H "Content-Type: application/json" \
  -d '{"credit_id": "VCS-2024-001"}'
```

### Bulk Verification
```bash
curl -X POST https://carboncheck-backend-production.up.railway.app/api/verify/bulk \
  -H "Content-Type: application/json" \
  -d '{"credit_ids": ["VCS-2024-001", "GOLD-2023-556"]}'
```

### Leaderboard
```bash
curl https://carboncheck-backend-production.up.railway.app/api/leaderboard?limit=10
```

---

## 🎯 Next Actions

1. ✅ Backend - Already deployed
2. ⏳ Supabase - Run SQL to create tables (5 min)
3. ⏳ Frontend - Deploy to Vercel (15 min)
4. ⏳ Testing - Run all tests
5. ⏳ Update FRONTEND_URL in Railway

---

## 📞 Service URLs

| Service | URL |
|---------|-----|
| Backend API | https://carboncheck-backend-production.up.railway.app |
| Backend Docs | https://carboncheck-backend-production.up.railway.app/docs |
| Supabase DB | https://oyevylxqjeokjfsuacau.supabase.co |
| Frontend | TBD after Vercel deployment |

---

## 💡 Key Decisions

1. Removed Registry-Service - Not needed for verification-only
2. Removed Integration-Layer - Merged into backend
3. Using Supabase - Instead of Railway Postgres
4. Three Services Only - Frontend, Backend, Database

---

## 🚨 Important Notes

- DO NOT deploy registry-service or integration-layer
- DO NOT create Railway Postgres (using Supabase)
- Backend has all verification logic
- Frontend calls backend directly
- Supabase for caching and leaderboard only

---

## 📝 Session Status

**Last Updated:** 2026-03-28
**Branch:** 001-carboncheck-trust-journeys
**Phase:** Step 2 (Supabase setup pending)

Continue from Step 2: Supabase Database Setup

---

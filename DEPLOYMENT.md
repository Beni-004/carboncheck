# CarbonCheck Deployment Guide

Complete deployment guide for the CarbonCheck monorepo with Vercel (frontend) and Railway (backend services).

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│                    apps/web (Vercel)                        │
│                   https://carboncheck.vercel.app            │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ├──────────────────────────────────┐
                  ▼                                  ▼
┌─────────────────────────────┐    ┌─────────────────────────────┐
│     Backend (Railway)       │    │  Integration Layer          │
│  Main API - backend/        │◄───┤  integration-layer/         │
│  Port: 8000                 │    │  Port: 8000                 │
└────────┬────────────────────┘    └──────────┬──────────────────┘
         │                                    │
         │                                    ▼
         │                         ┌─────────────────────────────┐
         │                         │  Registry Service           │
         │                         │  registry-service/          │
         │                         │  Port: 3000                 │
         │                         └──────────┬──────────────────┘
         │                                    │
         └────────────┬───────────────────────┘
                      ▼
         ┌──────────────────────────┐
         │   Supabase PostgreSQL    │
         │   (Database)             │
         └──────────────────────────┘
```

## Deployment Matrix

| Service | Platform | Root Directory | Port | Database |
|---------|----------|----------------|------|----------|
| Frontend | Vercel | `apps/web` | 3000 | None |
| Backend | Railway | `backend` | $PORT (Railway) | Supabase |
| Integration Layer | Railway | `integration-layer` | $PORT (Railway) | Supabase |
| Registry Service | Railway | `registry-service` | $PORT (Railway) | Railway PostgreSQL |

---

## Prerequisites

### Accounts & Services
- [x] **Vercel Account** for frontend hosting
- [x] **Railway Account** for backend services
- [x] **Supabase Account** for main database
- [x] **GitHub Account** with repository access
- [ ] **Sentinel Hub Account** (optional - for live satellite data)

### Local Setup (Optional)
```bash
# Clone repository
git clone https://github.com/your-org/carboncheck.git
cd carboncheck

# Install Vercel CLI
npm install -g vercel

# Install Railway CLI
npm install -g @railway/cli
```

---

## Deployment Order

**IMPORTANT**: Deploy services in this order to ensure proper dependencies:

1. **Database Setup** (Supabase + Railway PostgreSQL)
2. **Registry Service** (needs database)
3. **Backend Service** (needs database)
4. **Integration Layer** (needs Registry Service + Backend)
5. **Frontend** (needs Backend URL)

---

## 1. Database Setup

### 1.1 Supabase (Main Database)

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Note your project URL and service role key:
   - **URL**: `https://your-project.supabase.co`
   - **Service Key**: Settings → API → `service_role` key (secret)

3. Run database migrations (optional):
   ```bash
   cd backend
   python apply_migration.py
   ```

### 1.2 Railway PostgreSQL (Registry Database)

This will be created automatically when deploying the Registry Service.

---

## 2. Registry Service Deployment (Railway)

### 2.1 Create Service
1. Go to [railway.app](https://railway.app)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository and click **"Deploy"**

### 2.2 Add PostgreSQL Database
1. In your Railway project, click **"New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway will automatically create database and set environment variables

### 2.3 Configure Service
**Settings → Root Directory:**
```
registry-service
```

**Settings → Build & Start:**
- Build Command: (leave empty)
- Start Command: (leave empty)

### 2.4 Set Environment Variables
**Variables tab:**
```bash
# Database (automatically set by Railway)
REGISTRY_DB_HOST=${{Postgres.PGHOST}}
REGISTRY_DB_PORT=${{Postgres.PGPORT}}
REGISTRY_DB_USER=${{Postgres.PGUSER}}
REGISTRY_DB_PASSWORD=${{Postgres.PGPASSWORD}}
REGISTRY_DB_NAME=${{Postgres.PGDATABASE}}

# Application
NODE_ENV=production
SYSTEM_COUNTRY=NG
SYSTEM_COUNTRY_NAME=Nigeria
DEFAULT_CREDIT_UNIT=tCO2e
```

### 2.5 Deploy & Verify
```bash
# Check deployment status in Railway dashboard
# Note the public URL: https://registry-service-production.up.railway.app

# Verify health
curl https://your-registry-service.railway.app/api/v1/health
```

**Expected Response:**
```json
{"status": "ok", "info": {"database": {"status": "up"}}}
```

---

## 3. Backend Service Deployment (Railway)

### 3.1 Create New Service
1. In the same Railway project, click **"New"** → **"GitHub Repo"**
2. Select the same repository (creates service #2)

### 3.2 Configure Service
**Settings → Root Directory:**
```
backend
```

### 3.3 Set Environment Variables
**Variables tab:**
```bash
# Supabase (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key

# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# CORS (set after deploying frontend)
FRONTEND_URL=https://carboncheck.vercel.app

# Sentinel Hub (Optional - for live satellite data)
SENTINEL_CLIENT_ID=your-sentinel-client-id
SENTINEL_CLIENT_SECRET=your-sentinel-client-secret
SENTINEL_API_URL=https://sh.dataspace.copernicus.eu/api/v1/process

# API Configuration
EXTERNAL_API_TIMEOUT=15
BULK_VERIFY_MAX_IDS=50
```

### 3.4 Deploy & Verify
```bash
# Note the public URL: https://backend-production.up.railway.app

# Check health
curl https://your-backend.railway.app/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "integrations": {
    "database": {"status": "operational"},
    "sentinel_hub": {"status": "operational" or "unavailable"},
    "verra_registry": {"status": "operational"}
  }
}
```

---

## 4. Integration Layer Deployment (Railway)

### 4.1 Create New Service
1. In the same Railway project, click **"New"** → **"GitHub Repo"**
2. Select the same repository (creates service #3)

### 4.2 Configure Service
**Settings → Root Directory:**
```
integration-layer
```

### 4.3 Set Environment Variables
**Variables tab:**
```bash
# Registry Service (from step 2)
REGISTRY_SERVICE_URL=https://your-registry-service.railway.app
REGISTRY_TIMEOUT=30

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key

# Sentinel Hub (Optional - same as backend)
SATELLITE_API_ENABLED=true
SENTINEL_CLIENT_ID=your-sentinel-client-id
SENTINEL_CLIENT_SECRET=your-sentinel-client-secret
SENTINEL_API_URL=https://sh.dataspace.copernicus.eu/api/v1/process

# Feature Flags
ENABLE_AUTO_VERIFICATION=false
ENABLE_REGISTRY_SYNC=true
```

### 4.4 Deploy & Verify
```bash
# Note the public URL: https://integration-layer-production.up.railway.app

# Check health
curl https://your-integration-layer.railway.app/health
```

---

## 5. Frontend Deployment (Vercel)

### 5.1 Import Repository
1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repository
3. Vercel will detect Next.js automatically

### 5.2 Configure Project
**Settings:**
- **Framework Preset**: Next.js (auto-detected)
- **Root Directory**: `apps/web`
- **Build Command**: `npm run build` (auto-detected)
- **Install Command**: `npm install` (auto-detected)
- **Output Directory**: `.next` (auto-detected)

### 5.3 Set Environment Variables
**Settings → Environment Variables:**

Add for **Production, Preview, and Development**:

```bash
# Required
NEXT_PUBLIC_API_URL=https://your-backend.railway.app

# Optional (for full integration)
NEXT_PUBLIC_INTEGRATION_API_URL=https://your-integration-layer.railway.app
NEXT_PUBLIC_REGISTRY_API_URL=https://your-registry-service.railway.app
```

### 5.4 Deploy
```bash
# Via Git push (automatic)
git push origin main

# Or via Vercel CLI
cd apps/web
vercel --prod
```

### 5.5 Verify Deployment
1. Visit your Vercel URL: `https://carboncheck.vercel.app`
2. Go to `/verify` page
3. Enter a test credit ID: `VCS-2024-001`
4. Check that data comes from "Live API" (not mock)

### 5.6 Update Backend CORS
After frontend is deployed, update Backend's `FRONTEND_URL`:

**Railway → Backend Service → Variables:**
```bash
FRONTEND_URL=https://carboncheck.vercel.app
```

Redeploy backend for CORS changes to take effect.

---

## Environment Variables Reference

### Frontend (apps/web)
| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | ✅ Yes | `https://backend.railway.app` | Main backend API |
| `NEXT_PUBLIC_INTEGRATION_API_URL` | ⚠️ Optional | `https://integration.railway.app` | Integration layer |
| `NEXT_PUBLIC_REGISTRY_API_URL` | ⚠️ Optional | `https://registry.railway.app` | Registry service |

### Backend (backend)
| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `SUPABASE_URL` | ✅ Yes | `https://proj.supabase.co` | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | ✅ Yes | `eyJhb...` | Service role key |
| `FRONTEND_URL` | ⚠️ Optional | `https://app.vercel.app` | For CORS |
| `SENTINEL_CLIENT_ID` | ⚠️ Optional | `cdse-client-id` | Sentinel Hub OAuth |
| `SENTINEL_CLIENT_SECRET` | ⚠️ Optional | `secret...` | Sentinel Hub OAuth |
| `ENVIRONMENT` | ⚠️ Optional | `production` | Environment mode |
| `DEBUG` | ⚠️ Optional | `false` | Debug mode |
| `LOG_LEVEL` | ⚠️ Optional | `WARNING` | Log level |

### Integration Layer (integration-layer)
| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `REGISTRY_SERVICE_URL` | ✅ Yes | `https://registry.railway.app` | Registry service URL |
| `SUPABASE_URL` | ✅ Yes | `https://proj.supabase.co` | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | ✅ Yes | `eyJhb...` | Service role key |
| `SENTINEL_CLIENT_ID` | ⚠️ Optional | `cdse-client-id` | Sentinel Hub OAuth |
| `SENTINEL_CLIENT_SECRET` | ⚠️ Optional | `secret...` | Sentinel Hub OAuth |
| `SATELLITE_API_ENABLED` | ⚠️ Optional | `true` | Enable satellite |
| `ENABLE_AUTO_VERIFICATION` | ⚠️ Optional | `false` | Auto-verify projects |
| `ENABLE_REGISTRY_SYNC` | ⚠️ Optional | `true` | Sync with registry |

### Registry Service (registry-service)
| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `REGISTRY_DB_HOST` | ✅ Yes | `${{Postgres.PGHOST}}` | Database host |
| `REGISTRY_DB_PORT` | ✅ Yes | `${{Postgres.PGPORT}}` | Database port |
| `REGISTRY_DB_USER` | ✅ Yes | `${{Postgres.PGUSER}}` | Database user |
| `REGISTRY_DB_PASSWORD` | ✅ Yes | `${{Postgres.PGPASSWORD}}` | Database password |
| `REGISTRY_DB_NAME` | ✅ Yes | `${{Postgres.PGDATABASE}}` | Database name |
| `NODE_ENV` | ⚠️ Optional | `production` | Environment mode |
| `SYSTEM_COUNTRY` | ⚠️ Optional | `NG` | Country code |
| `SYSTEM_COUNTRY_NAME` | ⚠️ Optional | `Nigeria` | Country name |

---

## Testing the Full Stack

### 1. Test Registry Service
```bash
curl https://your-registry.railway.app/api/v1/programmes
```

### 2. Test Backend API
```bash
curl -X POST https://your-backend.railway.app/api/verify \
  -H "Content-Type: application/json" \
  -d '{"credit_id": "VCS-2024-001"}'
```

### 3. Test Integration Layer
```bash
curl https://your-integration-layer.railway.app/api/registry/projects
```

### 4. Test Frontend
1. Visit `https://carboncheck.vercel.app`
2. Navigate to `/verify`
3. Enter credit ID: `VCS-2024-001`
4. Verify trust score is calculated
5. Check data source badge shows "Live API"

---

## Troubleshooting

### Frontend Issues

**Problem**: Frontend shows mock data instead of live API data
- **Check**: Verify `NEXT_PUBLIC_API_URL` is set in Vercel
- **Check**: Ensure backend is accessible (test `/health` endpoint)
- **Check**: Look for CORS errors in browser console
- **Fix**: Update backend's `FRONTEND_URL` to include Vercel URL

**Problem**: Build fails on Vercel
- **Check**: Ensure `package.json` has all dependencies
- **Check**: Verify TypeScript compiles locally: `npm run build`
- **Check**: Review Vercel build logs for specific errors

### Backend Issues

**Problem**: Database connection fails
- **Check**: Verify `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` are correct
- **Check**: Test Supabase project is active
- **Check**: Ensure service role key has necessary permissions

**Problem**: Satellite data unavailable
- **Expected**: If `SENTINEL_CLIENT_ID` not set, system uses mock data
- **Check**: Health endpoint shows `sentinel_hub.status: "unavailable"`
- **Fix**: Register at [dataspace.copernicus.eu](https://dataspace.copernicus.eu/) and add credentials

**Problem**: CORS errors
- **Check**: `FRONTEND_URL` is set in backend variables
- **Check**: Frontend URL matches exactly (including https://)
- **Fix**: Redeploy backend after updating CORS settings

### Integration Layer Issues

**Problem**: Cannot connect to Registry Service
- **Check**: Verify `REGISTRY_SERVICE_URL` is correct
- **Check**: Ensure Registry Service is deployed and running
- **Check**: Test Registry Service health endpoint directly

**Problem**: Verification returns errors
- **Check**: All dependent services (backend, registry) are running
- **Check**: Environment variables are set correctly
- **Fix**: Review logs for specific error messages

### Registry Service Issues

**Problem**: Database connection fails
- **Check**: All `REGISTRY_DB_*` variables are set
- **Check**: Railway PostgreSQL service is running
- **Check**: Database credentials are correct

**Problem**: Tables not created
- **Fix**: Ensure `NODE_ENV=development` for auto-sync, OR
- **Fix**: Run migrations: `railway run npm run migration:run`

---

## Monitoring & Maintenance

### Health Checks
Set up monitoring for these endpoints:

- **Backend**: `https://your-backend.railway.app/health`
- **Integration**: `https://your-integration-layer.railway.app/health`
- **Registry**: `https://your-registry.railway.app/api/v1/health`
- **Frontend**: `https://carboncheck.vercel.app`

### Recommended Tools
- **Uptime Monitoring**: UptimeRobot, Pingdom, or Better Uptime
- **Error Tracking**: Sentry (add to each service)
- **Analytics**: Vercel Analytics (free for frontend)

### Logs Access

**Railway:**
```bash
# Via Railway CLI
railway login
railway link
railway logs

# Or view in Railway Dashboard → Deployments → Logs
```

**Vercel:**
```bash
# Via Vercel CLI
vercel logs [deployment-url]

# Or view in Vercel Dashboard → Deployments → Logs
```

### Database Backups

**Supabase:**
- Automatic daily backups (retained for 7 days on free plan)
- Manual backups: Dashboard → Database → Backups

**Railway PostgreSQL:**
- Automatic daily backups (retained for 7 days)
- Manual backups: Railway Dashboard → Database → Backups

---

## Scaling Considerations

### Vercel (Frontend)
- Automatic edge caching
- Global CDN distribution
- Automatic scaling (no configuration needed)

### Railway (Backend Services)
- **Free Tier**: 500 hours/month, $5 credit
- **Pro Plan**: Automatic scaling, pay-as-you-go
- **Horizontal Scaling**: Add replicas in service settings
- **Vertical Scaling**: Upgrade plan for more resources

### Database
- **Supabase Free Tier**: 500MB database, 50,000 rows
- **Upgrade**: As data grows, upgrade to Pro ($25/month)
- **Railway PostgreSQL**: Scales with Railway plan

---

## Cost Estimates

### Minimal Setup (Development/Demo)
- **Vercel**: Free (hobby plan)
- **Railway**: $5-10/month (3 services)
- **Supabase**: Free tier
- **Total**: ~$5-10/month

### Production Setup
- **Vercel**: $20/month (Pro plan)
- **Railway**: $20-50/month (pro plan, 3 services)
- **Supabase**: $25/month (Pro plan)
- **Total**: ~$65-95/month

### High-Traffic Production
- **Vercel**: Custom pricing
- **Railway**: $100-300/month (scaled services)
- **Supabase**: Custom pricing
- **Total**: $200-500/month

---

## CI/CD Pipeline

### Automatic Deployments

**Vercel (Frontend):**
- Deploys automatically on push to `main` (production)
- Preview deployments for all pull requests
- No configuration needed

**Railway (Backend Services):**
- Deploys automatically on push to `main`
- Manual deployments via "Deploy" button
- Can configure deploy branches in settings

### Manual Deployments

**Railway CLI:**
```bash
railway up
```

**Vercel CLI:**
```bash
vercel --prod
```

---

## Security Checklist

- [x] All secrets stored in platform environment variables (not in code)
- [x] Supabase service role key kept secret (never exposed to frontend)
- [x] Database credentials secured in Railway/Supabase
- [x] CORS configured to allow only known origins
- [x] HTTPS enforced on all services (automatic on Railway/Vercel)
- [x] `NODE_ENV=production` set for all production services
- [x] Database auto-sync disabled in production (`NODE_ENV=production`)
- [x] No hardcoded URLs in code (all use environment variables)

---

## Support

### Documentation
- **Frontend**: `apps/web/README.md`
- **Backend**: `backend/README.md`
- **Integration Layer**: `integration-layer/README.md`
- **Registry Service**: `registry-service/README.md`

### Platform Support
- **Vercel**: [vercel.com/support](https://vercel.com/support)
- **Railway**: [railway.app/help](https://railway.app/help)
- **Supabase**: [supabase.com/docs](https://supabase.com/docs)

---

## Quick Reference

### Service URLs (Update after deployment)
```bash
# Frontend
FRONTEND_URL=https://carboncheck.vercel.app

# Backend Services
BACKEND_URL=https://backend-production.up.railway.app
INTEGRATION_URL=https://integration-production.up.railway.app
REGISTRY_URL=https://registry-production.up.railway.app

# Database
SUPABASE_URL=https://your-project.supabase.co
```

### Essential Commands
```bash
# Railway
railway login
railway link
railway logs
railway status
railway up

# Vercel
vercel login
vercel link
vercel logs
vercel --prod

# Health checks
curl $BACKEND_URL/health
curl $INTEGRATION_URL/health
curl $REGISTRY_URL/api/v1/health
```

---

**Last Updated**: 2026-03-28
**Repository**: https://github.com/your-org/carboncheck
**License**: MIT

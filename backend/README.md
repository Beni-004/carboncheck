# CarbonCheck Backend API

FastAPI backend service for carbon credit verification and trust scoring.

## Features

- **Credit Verification**: Individual carbon credit verification with trust scoring
- **Bulk Audit**: Batch verification for up to 50 credits
- **Public Leaderboard**: Hall of shame for flagged credits
- **Health Checks**: Comprehensive health endpoint with integration status
- **Automated Fallback**: Intelligent caching when external APIs are unavailable

## Tech Stack

- **Framework**: FastAPI 0.109+
- **Server**: Uvicorn with standard extras
- **Database**: Supabase (PostgreSQL)
- **Satellite Data**: Sentinel Hub (Copernicus Data Space)
- **AI/ML**: PyTorch, scikit-learn, XGBoost
- **Geospatial**: GeoPandas, Rasterio, Shapely

## Getting Started

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the server
uvicorn app.main:app --reload --port 8000
```

Visit http://localhost:8000/docs for interactive API documentation.

### Environment Variables

See `.env.example` for all available configuration options.

**Required:**
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_KEY`: Service role key for database access

**Optional:**
- `SENTINEL_CLIENT_ID`: Sentinel Hub OAuth client ID
- `SENTINEL_CLIENT_SECRET`: Sentinel Hub OAuth secret
- `FRONTEND_URL`: Frontend URL for CORS configuration

## API Endpoints

### Core Endpoints
- `GET /` - API information
- `GET /health` - Health check with integration status
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

### Verification
- `POST /api/verify` - Verify single carbon credit
- `POST /api/verify/bulk` - Bulk verify up to 50 credits

### Leaderboard
- `GET /api/leaderboard` - Get public leaderboard of flagged credits

## Production Deployment (Railway)

### Prerequisites
1. A Railway account ([railway.app](https://railway.app))
2. A Supabase project ([supabase.com](https://supabase.com))
3. (Optional) Sentinel Hub account for satellite data

### Deployment Steps

#### 1. Create Railway Project
```bash
# Option A: Deploy via Railway Dashboard
# - Go to railway.app/new
# - Select "Deploy from GitHub repo"
# - Choose your repository

# Option B: Deploy via Railway CLI
railway login
railway init
railway up
```

#### 2. Configure Root Directory
In Railway project settings:
- **Root Directory**: `backend`
- **Build Command**: (leave empty - Docker will handle it)
- **Start Command**: (leave empty - Dockerfile CMD will be used)

#### 3. Set Environment Variables
In Railway Dashboard → Variables tab:

**Required:**
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
ENVIRONMENT=production
DEBUG=false
```

**Optional but Recommended:**
```bash
FRONTEND_URL=https://your-app.vercel.app
SENTINEL_CLIENT_ID=your-sentinel-client-id
SENTINEL_CLIENT_SECRET=your-sentinel-client-secret
LOG_LEVEL=WARNING
```

**Important Notes:**
- Railway automatically sets `PORT` - do not override it
- Never commit secrets to the repository
- Use Railway's secret management for sensitive values
- Set `ENVIRONMENT=production` to disable verbose logging

#### 4. Database Setup
The backend uses Supabase for data storage:

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Run database migrations (if any):
   ```bash
   python apply_migration.py  # Run locally or via Railway shell
   ```
3. Copy the service role key (Settings → API → service_role key)
4. Add `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` to Railway

#### 5. Deploy
```bash
# Automatic deployment via Git push
git push origin main

# Or trigger manual deployment
railway up

# Or redeploy from Railway dashboard
# → Deployments tab → Deploy
```

### Post-Deployment Verification

#### 1. Check Health Endpoint
```bash
curl https://your-backend.railway.app/health
```

Expected response:
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

#### 2. Test Verification Endpoint
```bash
curl -X POST https://your-backend.railway.app/api/verify \
  -H "Content-Type: application/json" \
  -d '{"credit_id": "VCS-2024-001"}'
```

#### 3. Check Logs
```bash
# Via Railway CLI
railway logs

# Or view in Railway Dashboard → Deployments tab
```

### Monitoring and Troubleshooting

#### Common Issues

**Issue: Build fails with "Module not found"**
- Check that `requirements.txt` includes all dependencies
- Verify Python version compatibility (requires 3.11+)
- Check Railway build logs for specific error

**Issue: Database connection fails**
- Verify `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` are set correctly
- Check Supabase project status
- Ensure service role key has necessary permissions

**Issue: Satellite data unavailable**
- This is expected if `SENTINEL_CLIENT_ID` is not set
- The system will use deterministic mock satellite data as fallback
- Health endpoint will show `sentinel_hub.status: "unavailable"`

**Issue: CORS errors from frontend**
- Set `FRONTEND_URL` environment variable to your Vercel URL
- Include both production and preview URLs if needed
- Check that frontend is using correct backend URL

#### Performance Optimization

- **Caching**: System automatically caches registry and satellite data
- **Timeouts**: Configure `EXTERNAL_API_TIMEOUT` for API resilience
- **Batch Limits**: Adjust `BULK_VERIFY_MAX_IDS` based on performance
- **Database**: Ensure Supabase indexes are set up for fast queries

#### Monitoring
- Use Railway's built-in metrics dashboard
- Monitor `/health` endpoint for integration status
- Set up uptime monitoring (UptimeRobot, Pingdom, etc.)
- Review Railway logs for errors and warnings

### Scaling
Railway automatically handles:
- Horizontal scaling (multiple replicas)
- Load balancing
- Zero-downtime deployments
- Automatic HTTPS certificates

For high-traffic scenarios:
1. Enable Railway's autoscaling
2. Upgrade to a larger plan
3. Optimize database queries
4. Consider adding Redis for caching

### Cost Optimization
- Use `LOG_LEVEL=WARNING` in production to reduce log volume
- Set appropriate `EXTERNAL_API_TIMEOUT` to avoid hanging requests
- Monitor Railway usage dashboard
- Consider using Supabase connection pooling

## Development

### Project Structure
```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── db.py                # Database client
│   ├── routers/             # API endpoints
│   │   ├── verify.py        # Verification endpoints
│   │   └── leaderboard.py   # Leaderboard endpoints
│   ├── services/            # Business logic
│   ├── clients/             # External API clients
│   ├── middleware/          # Custom middleware
│   └── verification_engine/ # Core verification logic
├── requirements.txt         # Python dependencies
├── Dockerfile              # Production container
└── .dockerignore           # Docker build exclusions
```

### Running Tests
```bash
pytest
pytest --cov=app tests/  # With coverage
```

### Local Docker Build
```bash
# Build image
docker build -t carboncheck-backend .

# Run container
docker run -p 8000:8000 \
  -e SUPABASE_URL=your-url \
  -e SUPABASE_SERVICE_KEY=your-key \
  carboncheck-backend
```

## API Documentation

### Verify Single Credit
```bash
POST /api/verify
Content-Type: application/json

{
  "credit_id": "VCS-2024-001"
}
```

Response:
```json
{
  "credit_id": "VCS-2024-001",
  "trust_score": 92,
  "verdict": "PASS",
  "checks": {
    "registry_verified": true,
    "satellite_match": true,
    "ai_prediction_valid": true,
    "anomaly_score_low": true
  },
  "fraud_risks": [],
  "data_sources": ["Verra Registry", "Sentinel Hub", "AI Model"]
}
```

### Bulk Verify
```bash
POST /api/verify/bulk
Content-Type: application/json

{
  "credit_ids": ["VCS-2024-001", "GOLD-2023-556", "ACR-2021-999"]
}
```

### Leaderboard
```bash
GET /api/leaderboard?category=Renewable%20Energy&limit=10
```

## License

MIT

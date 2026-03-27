# CarbonCheck Integration Layer

FastAPI service that bridges the CarbonCheck verification system with the UNDP National Carbon Registry.

## Features

- **Registry Integration**: Sync and manage carbon projects from UNDP Registry
- **Verification Pipeline**: Automated trust score calculation for registry projects
- **Multi-Layer Analysis**: Ground, Satellite, AI, and Scoring layers
- **Leaderboard Generation**: Project ranking based on verification results
- **Statistics Dashboard**: Aggregated project and verification statistics

## Tech Stack

- **Framework**: FastAPI
- **Server**: Uvicorn
- **Database**: Supabase (via CarbonCheck backend)
- **Registry**: UNDP National Carbon Registry Service
- **Satellite Data**: Sentinel Hub (Copernicus Data Space)

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
uvicorn app.main:app --reload --port 8001
```

Visit http://localhost:8001/docs for interactive API documentation.

### Environment Variables

See `.env.example` for all available configuration options.

**Required:**
- `REGISTRY_SERVICE_URL`: URL of the UNDP Registry Service
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_KEY`: Service role key for database access

**Optional:**
- `SENTINEL_CLIENT_ID`: Sentinel Hub OAuth client ID
- `SENTINEL_CLIENT_SECRET`: Sentinel Hub OAuth secret
- `SATELLITE_API_ENABLED`: Enable/disable satellite verification (default: true)
- `ENABLE_AUTO_VERIFICATION`: Auto-verify new projects (default: false)
- `ENABLE_REGISTRY_SYNC`: Enable registry synchronization (default: true)

## API Endpoints

### Core
- `GET /` - Service information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

### Registry Management
- `GET /api/registry/projects` - List all projects from registry
- `GET /api/registry/projects/{id}` - Get project details
- `POST /api/registry/projects/{id}/verify` - Verify specific project
- `POST /api/registry/verify-all` - Verify all projects

### Analytics
- `GET /api/registry/leaderboard` - Get project leaderboard
- `GET /api/registry/statistics` - Get verification statistics

## Production Deployment (Railway)

### Prerequisites
1. Railway account ([railway.app](https://railway.app))
2. Deployed Registry Service (see `registry-service/README.md`)
3. Supabase project

### Deployment Steps

#### 1. Create Railway Service
```bash
# Via Railway Dashboard
# - Go to railway.app/new
# - Select "Deploy from GitHub repo"
# - Choose your repository

# Or via Railway CLI
railway login
railway init
railway up
```

#### 2. Configure Root Directory
In Railway project settings:
- **Root Directory**: `integration-layer`
- **Build Command**: (leave empty - Docker will handle it)
- **Start Command**: (leave empty - Dockerfile CMD will be used)

#### 3. Set Environment Variables
In Railway Dashboard → Variables tab:

**Required:**
```bash
REGISTRY_SERVICE_URL=https://your-registry.railway.app
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
```

**Optional:**
```bash
SENTINEL_CLIENT_ID=your-sentinel-client-id
SENTINEL_CLIENT_SECRET=your-sentinel-client-secret
SATELLITE_API_ENABLED=true
ENABLE_AUTO_VERIFICATION=false
ENABLE_REGISTRY_SYNC=true
REGISTRY_TIMEOUT=30
```

**Important Notes:**
- Railway automatically sets `PORT` - do not override it
- Deploy Registry Service before Integration Layer
- Ensure Registry Service URL is accessible
- Never commit secrets to the repository

#### 4. Deploy
```bash
# Automatic deployment via Git push
git push origin main

# Or via Railway CLI
railway up

# Or redeploy from Railway dashboard
```

### Post-Deployment Verification

#### 1. Check Health
```bash
curl https://your-integration-layer.railway.app/health
```

#### 2. List Projects
```bash
curl https://your-integration-layer.railway.app/api/registry/projects
```

#### 3. Verify a Project
```bash
curl -X POST https://your-integration-layer.railway.app/api/registry/projects/1/verify
```

#### 4. Check Logs
```bash
railway logs
```

### Troubleshooting

**Issue: Cannot connect to Registry Service**
- Verify `REGISTRY_SERVICE_URL` is correct
- Ensure Registry Service is deployed and running
- Check Registry Service logs for errors
- Test Registry Service health endpoint directly

**Issue: Database connection fails**
- Verify `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`
- Check Supabase project status
- Ensure service role key has necessary permissions

**Issue: Satellite verification unavailable**
- This is expected if Sentinel Hub credentials are not set
- System will use mock satellite data as fallback
- Set `SENTINEL_CLIENT_ID` and `SENTINEL_CLIENT_SECRET` for live data

**Issue: Verification returns errors**
- Check that all dependent services are running
- Verify environment variables are set correctly
- Review logs for specific error messages
- Test each layer independently

### Monitoring
- Monitor `/health` endpoint
- Use Railway's metrics dashboard
- Set up alerts for service failures
- Review logs regularly for errors

## Architecture

### Verification Pipeline
1. **Ground Layer**: Fetch project data from Registry Service
2. **Satellite Layer**: Analyze NDVI via Sentinel Hub
3. **AI Layer**: CO2 prediction and anomaly detection
4. **Scoring Layer**: Calculate trust score (0-100)

### Data Flow
```
Registry Service → Integration Layer → CarbonCheck Backend → Supabase
                          ↓
                   Sentinel Hub API
                          ↓
                    AI/ML Processing
```

## Development

### Project Structure
```
integration-layer/
├── app/
│   ├── main.py              # FastAPI application
│   ├── routers/
│   │   └── registry_router.py  # Registry endpoints
│   ├── services/            # Business logic
│   └── clients/             # External API clients
├── requirements.txt         # Python dependencies
├── Dockerfile              # Production container
└── .dockerignore           # Docker build exclusions
```

### Running Tests
```bash
pytest
```

### Local Docker Build
```bash
docker build -t carboncheck-integration .
docker run -p 8001:8000 \
  -e REGISTRY_SERVICE_URL=http://host.docker.internal:3001 \
  -e SUPABASE_URL=your-url \
  -e SUPABASE_SERVICE_KEY=your-key \
  carboncheck-integration
```

## API Documentation

### Verify Project
```bash
POST /api/registry/projects/{project_id}/verify
```

Response:
```json
{
  "project_id": "PRJ-001",
  "project_name": "Solar Power Plant",
  "trust_score": 87,
  "verdict": "PASS",
  "verification_layers": {
    "ground": {"status": "verified", "data_complete": true},
    "satellite": {"status": "verified", "ndvi_match": true},
    "ai": {"status": "verified", "prediction_valid": true},
    "scoring": {"final_score": 87, "checks_passed": 4}
  },
  "verified_at": "2026-03-28T00:00:00Z"
}
```

### Get Leaderboard
```bash
GET /api/registry/leaderboard?category=Renewable%20Energy&limit=10
```

### Get Statistics
```bash
GET /api/registry/statistics
```

## License

MIT

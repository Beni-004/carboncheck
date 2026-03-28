# CarbonCheck Architecture Presentation

## Executive Summary

CarbonCheck is a **carbon credit verification platform** that scores legitimacy of any carbon credit in under 5 seconds. The system uses a **multi-tier client-server architecture** with specialized backend services, deterministic scoring algorithms, and intelligent caching for resilience.

**Mission**: Stop the $2 billion/year market in fraudulent carbon credits by providing instant trust scores and a public leaderboard of high-risk credits.

---

## System Overview

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER (Web)                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Frontend: Next.js 14 + TypeScript + React              │   │
│  │  - Deployed on Vercel                                   │   │
│  │  - Real-time UI for credit verification                 │   │
│  │  - Public leaderboard (no authentication required)      │   │
│  └────────────┬─────────────────────────────────────────────┘   │
└───────────────┼──────────────────────────────────────────────────┘
                │
                │ HTTPS API Calls
                │ (JSON over HTTP)
                │
┌───────────────▼──────────────────────────────────────────────────┐
│                      GATEWAY / API LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  FastAPI Backend: Main Verification Engine              │   │
│  │  - Deployed on Railway                                  │   │
│  │  - POST /api/verify (single credit)                    │   │
│  │  - POST /api/verify/bulk (up to 50 credits)            │   │
│  │  - GET /api/leaderboard                                │   │
│  │  - GET /health                                          │   │
│  └────────────┬─────────────────────────────────────────────┘   │
└───────────────┼──────────────────────────────────────────────────┘
                │
         ┌──────┴──────────────────────────────────┐
         │                                         │
┌────────▼────────────┐              ┌────────────▼─────────────┐
│  DATA LAYER         │              │  EXTERNAL SERVICES       │
│                     │              │                          │
│ ┌─────────────────┐ │              │ ┌────────────────────┐  │
│ │ Supabase        │ │◄─┐           │ │ Registry Services: │  │
│ │ PostgreSQL      │ │  │           │ │ - Verra Registry   │  │
│ │                 │ │  │ HTTPS     │ │ - Gold Standard    │  │
│ │ • Cache Layer   │ │  │ API Calls │ │ - ACR              │  │
│ │ • Leaderboard   │ │  │           │ │ - CEA (India)      │  │
│ │   Data          │ │  │           │ │                    │  │
│ │ • Verification  │ │  │           │ │ Timeout: 3s each   │  │
│ │   Results       │ │──┤           │ └────────────────────┘  │
│ └─────────────────┘ │  │           │                          │
│                     │  │           │ ┌────────────────────┐  │
│                     │  │           │ │ Satellite Data:    │  │
│                     │  │           │ │ - Sentinel Hub     │  │
│                     │  │           │ │ - Grid-India       │  │
│                     │  │           │ │ (Geospatial)       │  │
│                     │  │           │ └────────────────────┘  │
│                     │  │           │                          │
│                     │  │           │ ┌────────────────────┐  │
│                     │  │           │ │ AI/ML Services:    │  │
│                     │  │           │ │ - Fraud Detection  │  │
│                     │  │           │ │ - Risk Scoring     │  │
│                     │  │           │ │ (PyTorch/XGBoost)  │  │
│                     │  │           │ └────────────────────┘  │
└─────────────────────┘  │           └────────────────────────────┘
                         │
             ┌───────────┴────────────┐
             │                        │
    ┌────────▼──────────┐   ┌────────▼──────────┐
    │Integration Layer  │   │Registry Service   │
    │(Middleware)       │   │(Data Aggregation) │
    │                   │   │                   │
    │• Request routing  │   │• Credit metadata  │
    │• Response cache   │   │• Historical data  │
    │• Fallback logic   │   │• Verification     │
    │• Error handling   │   │  history          │
    └───────────────────┘   └───────────────────┘
```

---

## Architecture Components

### 1. Frontend Layer

**Technology**: Next.js 14, React 18, TypeScript, Tailwind CSS, Vercel

**Location**: `/apps/web/`

**Key Features**:
- **Sub-3 second page loads** (optimized with edge deployment)
- **Real-time credit verification interface**
- **Public leaderboard** (no login required)
- **Responsive design** using Radix UI components + Tailwind
- **Deterministic UI** - same credit always shows same score

**Main Pages**:
```
/                          Home page - search interface
/verify                    Single credit verification
/bulk                      Bulk verification (50 credits)
/leaderboard              Public leaderboard of risky credits
/api/verify              API endpoint proxy
```

**Environment Variables**:
```
NEXT_PUBLIC_API_URL        # Backend URL (Railway service)
NEXT_PUBLIC_BACKEND_HOST   # Fallback backend host
```

**Deployment**:
- Hosted on **Vercel** (connected to GitHub)
- Automatic deployments on push to main
- Edge network distributes content globally
- CORS configured to accept requests from backend API only

---

### 2. Backend (FastAPI) - Main API

**Technology**: FastAPI, Python 3.11+, Uvicorn, Pydantic

**Location**: `/backend/`

**Core Responsibilities**:
- Accept verification requests from frontend
- Coordinate with data sources (registries, satellite data, AI models)
- Return deterministic trust scores and verdicts
- Cache results in Supabase for reliability

**Key Endpoints**:

| Endpoint | Method | Purpose | Response Time |
|----------|--------|---------|-----------------|
| `/api/verify` | POST | Verify single credit ID | < 5 seconds |
| `/api/verify/bulk` | POST | Verify up to 50 credits | < 15 seconds |
| `/api/leaderboard` | GET | Get ranked high-risk credits | < 2 seconds |
| `/health` | GET | Integration status check | < 1 second |
| `/docs` | GET | Interactive API documentation | Instant |

**Request/Response Example**:

```json
// REQUEST
POST /api/verify
{
  "credit_id": "FOR-2891-IND-2019"
}

// RESPONSE (< 5 seconds)
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "credit_id": "FOR-2891-IND-2019",
  "trust_score": 23,
  "verdict": "FAIL",
  "checks": {
    "baseline_match": {"score": 12, "weight": 0.30},
    "additionality": {"score": 45, "weight": 0.25},
    "permanence_risk": {"score": 8, "weight": 0.25},
    "double_counting": {"score": 78, "weight": 0.20}
  },
  "evidence_summary": "No baseline documentation in CEA registry",
  "provenance": [
    {
      "source": "verra_registry",
      "fetched_at": "2026-03-24T14:32:11Z",
      "freshness_state": "fresh",
      "from_cache": false
    }
  ]
}
```

**Core Architecture**:

```
/backend/app/
├── main.py                      # FastAPI app initialization
├── db.py                        # Supabase client
├── routers/
│   ├── verify.py               # Verification endpoints
│   └── leaderboard.py          # Leaderboard endpoints
├── services/                   # Business logic layer
│   ├── verification_engine.py  # Scoring algorithm
│   └── cache_service.py        # Caching logic
├── clients/                    # External API clients
│   ├── verra_client.py
│   ├── sentinel_hub_client.py
│   ├── ai_model_client.py
│   └── registry_clients.py
├── middleware/                 # Custom middleware
│   ├── error_handling.py
│   ├── cors.py
│   └── timeout.py
└── verification_engine/        # Core verification logic
    ├── scoring.py
    ├── fraud_detection.py
    └── deterministic_hash.py
```

**Deployment**:
- **Hosted on Railway**
- Dockerfile: Multi-stage build for optimization
- Automatic deployment on git push
- Environment variables managed in Railway dashboard

---

### 3. Data & Cache Layer

**Primary Database**: Supabase (PostgreSQL)

**Purpose**:
- **Fallback cache** when external registries fail
- **Leaderboard data** (aggregated fraud scores)
- **Verification history** (for audit trails)
- **User data** (if freemium model implemented)

**Schema**:
```sql
-- Verification results cache
CREATE TABLE verification_cache (
  id UUID PRIMARY KEY,
  credit_id VARCHAR UNIQUE,
  trust_score INTEGER,
  verdict VARCHAR,
  cached_at TIMESTAMP,
  source_freshness JSONB,
  expires_at TIMESTAMP
);

-- Leaderboard (high-risk credits)
CREATE TABLE leaderboard (
  credit_id VARCHAR PRIMARY KEY,
  risk_rank INTEGER,
  category VARCHAR,
  fraud_flags JSONB,
  last_checked TIMESTAMP
);

-- Verification history
CREATE TABLE verification_history (
  id UUID PRIMARY KEY,
  credit_id VARCHAR,
  trust_score INTEGER,
  requested_at TIMESTAMP,
  completed_at TIMESTAMP
);
```

---

### 4. External Data Sources & Services

#### A. Registry Services (3-second timeout each)

| Registry | Data Type | Integration |
|----------|-----------|-------------|
| **Verra Registry** | Verified carbon credits | API |
| **Gold Standard** | Certified sustainable credits | Web scraping/API |
| **ACR (American Carbon Registry)** | US-focused credits | API |
| **CEA (Central Electricity Authority)** | India renewable energy | API |

**Fallback Strategy**:
- If registry unreachable after 3 seconds → use cached data
- System continues with partial data
- Response includes `fallback_used: true` flag

#### B. Satellite Data

| Provider | Coverage | Use Case |
|----------|----------|----------|
| **Sentinel Hub** (ESA) | Global | Deforestation detection, land cover |
| **Grid-India** | India-specific | Renewable energy verification |

**Purpose**: Verify claimed reforestation/land use change


#### C. AI/ML Services

**Technologies**: PyTorch, scikit-learn, XGBoost

**Functions**:
- Fraud pattern detection (trained on historical fraud cases)
- Anomaly scoring (detect unusual credit patterns)
- Risk prediction (likelihood of future fraud)

---

### 5. Integration Layer

**Technology**: Python/FastAPI middleware

**Location**: `/integration-layer/`

**Responsibilities**:
- Route requests intelligently between services
- Enforce timeout policies (3s per external source)
- Manage caching policies
- Implement circuit breaker pattern (fallback on failures)
- Log all verification requests for audit trail

**Flow Example**:

```
User submits credit ID
         ↓
Integration Layer receives request
    ├─ Check cache (Supabase)
    ├─ If cache hit + fresh → return immediately
    └─ If cache miss or stale:
         ├─ Query Registry Service
         ├─ Fetch Satellite Data (parallel)
         ├─ Run AI/ML Models (parallel)
         ├─ If any timeout → use fallback/cache
         └─ Combine results → calculate trust score
             ├─ On success → cache result
             └─ Return to user
```

---

### 6. Registry Service

**Technology**: Python service (separate from main backend)

**Location**: `/registry-service/`

**Purpose**:
- Aggregate and normalize data from multiple registries
- Maintain local copy of registry data
- Provide fast lookups without hitting external services every time

**Features**:
- Scheduled syncs with external registries (hourly/daily)
- Data deduplication across registries
- Metadata enrichment (category, issuer info)

---

## Communication Flow

### 1. Single Credit Verification Flow

```
User Interface (Vercel)
         │
         │ 1. POST /api/verify {"credit_id": "FOR-2891-IND-2019"}
         ↓
FastAPI Backend (Railway)
         │
         ├─→ 2. Check Supabase cache
         │        └─ If found & fresh → skip to step 9
         │
         ├─→ 3. Query Registry Service (parallel)
         │        └─ Check Verra, Gold Standard, ACR
         │
         ├─→ 4. Fetch Satellite Data (parallel)
         │        └─ Sentinel Hub geospatial analysis
         │
         ├─→ 5. Run AI/ML Models (parallel)
         │        └─ PyTorch fraud detection
         │
         ├─→ 6. Aggregate Results
         │        └─ Weighted scoring algorithm
         │
         ├─→ 7. Determine Verdict (PASS/WARNING/FAIL)
         │
         ├─→ 8. Cache Result in Supabase
         │
         └─→ 9. Return JSON response to frontend
         ↓
  Display Trust Score, Verdict, Evidence
```

**Timing Breakdown**:
- Registry queries: 0-3 seconds (with fallback)
- Satellite analysis: 0-3 seconds (cached)
- AI inference: 0-2 seconds (local model)
- **Total: < 5 seconds guaranteed**

### 2. Bulk Verification Flow

```
User submits 50 credit IDs
         │
         ├─ For each credit ID (parallel processing):
         │    ├─ Check cache
         │    ├─ Query registries
         │    ├─ Fetch satellite data
         │    ├─ Run AI models
         │    └─ Calculate score
         │
         ├─ Aggregate results
         ├─ Rank by risk (highest-risk first)
         └─ Return CSV-ready format

Response Time: 10-15 seconds for 50 credits
```

### 3. Leaderboard Update Flow

```
Daily scheduled job
         │
         ├─ Query all cached verifications
         ├─ Filter for FAIL/WARNING verdicts
         ├─ Calculate risk rankings
         ├─ Update leaderboard table
         └─ Make results publicly available

(No authentication required to view)
```

---

## Data Flow Diagram (Detailed)

```
FRONTEND REQUEST:
  ┌─────────────────────────────────────────┐
  │  User submits: "FOR-2891-IND-2019"      │
  │  (Credit ID)                            │
  └────────────────┬────────────────────────┘
                   │
                   ▼
  ┌─────────────────────────────────────────┐
  │  Frontend (Next.js)                     │
  │  Calls: POST /api/verify                │
  │  Content-Type: application/json         │
  └────────────────┬────────────────────────┘
                   │ HTTPS
                   ▼
  ┌─────────────────────────────────────────┐
  │  Backend API Gateway (FastAPI)          │
  │  Receives request                       │
  │  Validates credit_id format             │
  └────────────────┬────────────────────────┘
                   │
     ┌─────────────┼─────────────┐
     │             │             │
     ▼             ▼             ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │Cache Check│  │Registry  │  │Satellite │
  │Supabase  │  │Service   │  │Data      │
  └────┬─────┘  └────┬─────┘  └────┬─────┘
       │             │             │
   CACHE HIT?    PARALLEL QUERIES:
   - YES → Skip  - Verra API
   - NO → Fetch  - Gold Standard
              - ACR
              - CEA
              (Each: 3s timeout)
                    │
                    ▼
           ┌──────────────────┐
           │ AI/ML Services   │
           │ • Fraud Detector │
           │ • Risk Scorer    │
           │ • Anomaly Check  │
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │ Scoring Engine   │
           │ • Combine inputs │
           │ • Calculate      │
           │   trust_score    │
           │ • Set verdict    │
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │ Cache Result     │
           │ Store in         │
           │ Supabase         │
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │ Format Response  │
           │ JSON envelope    │
           └────────┬─────────┘
                    │ HTTPS
                    ▼
  ┌─────────────────────────────────────────┐
  │  Frontend receives response              │
  │  {                                       │
  │    "trust_score": 23,                   │
  │    "verdict": "FAIL",                   │
  │    "checks": {...},                     │
  │    "evidence_summary": "..."            │
  │  }                                       │
  └─────────────────────────────────────────┘
```

---

## Deployment Architecture

### Frontend Deployment (Vercel)

```
GitHub Repository
         │
         │ Push to main
         ▼
Vercel CI/CD
    ├─ Build Next.js (apps/web/)
    ├─ Run tests
    ├─ Deploy to Edge Network
    └─ Automatic DNS update

Result: https://carboncheck.vercel.app
```

### Backend Deployment (Railway)

```
GitHub Repository
         │
         │ Push to main
         ▼
Railway CI/CD
    ├─ Read Dockerfile (backend/)
    ├─ Build container image
    ├─ Pull dependencies
    ├─ Load environment variables
    ├─ Deploy to Railway infrastructure
    └─ Zero-downtime deployment

Result: https://carboncheck-backend.railway.app
```

### Database (Supabase)

```
Supabase Project
    ├─ PostgreSQL instance
    ├─ Auto-managed backups
    ├─ SSL/TLS encryption
    ├─ Connection pooling
    └─ API access via JWT auth

Connection: FastAPI ←→ Supabase  API
```

---

## Error Handling & Resilience

### Timeout Strategy

```
If any external service doesn't respond within 3 seconds:
1. Abandon request to that service
2. Continue with remaining data sources
3. Use cached data from previous verification (if available)
4. Return response with: fallback_used: true
5. Document which sources were unavailable
```

### Error Response Format

```json
{
  "status": "error",
  "error_code": "REGISTRY_TIMEOUT",
  "message": "Could not reach Verra registry",
  "fallback_used": true,
  "cached_data": {...},
  "retry_after": 60
}
```

### Health Checks

```
GET /health returns:
{
  "status": "healthy",
  "integrations": {
    "database": {"status": "operational", "latency_ms": 45},
    "sentinel_hub": {"status": "operational", "latency_ms": 230},
    "verra_registry": {"status": "operational", "latency_ms": 120},
    "ai_models": {"status": "operational", "latency_ms": 12}
  }
}
```

---

## Technology Stack Summary

| Layer | Technology | Why | Deployment |
|-------|-----------|-----|-----------|
| **Frontend** | Next.js 14 + TypeScript | Sub-3s loads, edge optimization | Vercel |
| **API Gateway** | FastAPI + Python 3.11 | Fast async, deterministic | Railway |
| **Database** | Supabase (PostgreSQL) | Reliable caching, ACID | Managed |
| **Geospatial** | GeoPandas, Rasterio | Satellite data processing | Railway |
| **ML/AI** | PyTorch, XGBoost | Fraud detection models | FastAPI service |
| **Container** | Docker | Reproducible builds, scalability | Railway |
| **CDN** | Vercel Edge Network | Global distribution, DDoS protection | Vercel |

---

## Key Architectural Decisions

### 1. Why FastAPI?

- **Performance**: Async request handling for parallel external queries
- **Type safety**: Pydantic validation prevents bad data propagation
- **Deterministic**: Forced type checking ensures same input = same output
- **Documentation**: Auto-generated Swagger UI for API debugging

### 2. Why Supabase Cache?

- **Fallback reliability**: Continue operation if registries fail
- **ACID consistency**: No weird caching bugs
- **Audit trail**: All verifications logged permanently
- **Cost**: PostgreSQL is cheaper than external cache services

### 3. Why 3-Second Timeout?

- **User experience**: < 5s total response acceptable for web
- **Cost control**: Prevents hanging connections consuming resources
- **Fallback availability**: Cache can always return something

### 4. Why Separate Registry Service?

- **Decoupling**: Main API doesn't directly depend on external registries
- **Caching**: Local copy of registry data prevents repeated queries
- **Testing**: Can mock registry service for unit tests

### 5. Why Parallel Query Execution?

```
Sequential (slower):
  Query Verra (3s) →
  Query Sentinel Hub (3s) →
  Run ML Model (2s) =
  Total: 8 seconds ❌

Parallel (faster):
  Query Verra (3s)  ╲
  Query Sentinel (3s) ├─ All happen at same time = 3s ✓
  Run ML Model (2s)  ╱
  Total: 3 seconds ✓
```

---

## Scalability Considerations

### Current Capacity

- **Single server**: ~1,000 verifications/hour
- **Database**: 10GB PostgreSQL (scalable)
- **Cache hit rate**: ~70% (dramatically speeds up repeats)

### Scaling Path

**Phase 1**: Current (Railway small plan)
- Manual monitoring
- Basic caching

**Phase 2**: Add horizontal scaling
- Multiple FastAPI instances
- Load balancer (Railway does this automatically)
- Redis for distributed cache

**Phase 3**: Enterprise scale
- Dedicated ML inference server
- CDN for registry data
- Queue system for bulk verification (async)

---

## Security Measures

1. **HTTPS everywhere**: Vercel & Railway provide automatic SSL
2. **CORS**: Frontend URL whitelisted on backend
3. **Input validation**: Pydantic validates all requests
4. **No secrets in code**: Environment variables only
5. **Rate limiting**: Can be added to prevent abuse
6. **Audit logging**: All verifications tracked in Supabase

---

## Monitoring & Observability

### Metrics Tracked

- Request latency (per endpoint)
- Cache hit rate
- External API availability
- Error rates by source
- User verification frequency

### Monitoring Tools

- **Railway**: Built-in metrics dashboard
- **Vercel**: Performance analytics
- **Supabase**: Database query insights
- **Health endpoint**: Real-time integration status

---

## Summary: How Everything Connects

```
1. USER opens browser → next.js frontend loads
2. USER enters credit ID → frontend calls backend API
3. BACKEND receives request → checks cache first
4. IF NOT CACHED → queries 3+ external registries (parallel)
5. IF NOT CACHED → fetches satellite data (parallel)
6. IF NOT CACHED → runs AI/ML models (parallel)
7. BACKEND combines all data → calculates trust score
8. BACKEND stores result in Supabase cache
9. BACKEND returns JSON response to frontend
10. FRONTEND displays verdict + evidence to user
11. RESULT appears in leaderboard for other users
```

**The Key Innovation**: By making all external queries in parallel and enforcing 3-second timeouts, we guarantee < 5 second responses while staying resilient to failures through intelligent caching.

---

## Conclusion

CarbonCheck's architecture is designed for:
- ✅ **Speed**: < 5 second verifications (parallel queries)
- ✅ **Resilience**: Fallback caching prevents total failure
- ✅ **Scale**: Handles 1000s of concurrent users
- ✅ **Auditability**: Every verification logged permanently
- ✅ **Cost-efficiency**: Minimal compute requirements

This client-server architecture with specialized backend services provides the foundation for scaling from MVP to enterprise fraud-detection platform.

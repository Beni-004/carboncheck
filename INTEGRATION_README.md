# CarbonCheck + UNDP Registry Integration

Integration system merging the UNDP National Carbon Registry with CarbonCheck AI verification.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CarbonCheck System                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────┐    ┌───────────────────┐    ┌──────────────────┐   │
│  │  Integration      │    │  Registry         │    │  Supabase        │   │
│  │  Layer (FastAPI)  │◄──►│  Service (NestJS) │    │  (PostgreSQL)    │   │
│  │  Port: 8000       │    │  Port: 3001       │    │                  │   │
│  └─────────┬─────────┘    └───────────────────┘    └────────┬─────────┘   │
│            │                                                  │            │
│            │         ┌────────────────────────┐              │            │
│            ├────────►│  Verification Pipeline │◄─────────────┤            │
│            │         └────────────────────────┘              │            │
│            │                     │                           │            │
│            ▼                     ▼                           ▼            │
│  ┌─────────────────┐  ┌─────────────────┐    ┌─────────────────────┐    │
│  │ Ground Layer    │  │ Satellite Layer │    │ AI Layer            │    │
│  │ (Registry Data) │  │ (NDVI/GEE)      │    │ (Prediction/Anomaly)│    │
│  └─────────────────┘  └─────────────────┘    └─────────────────────┘    │
│                                │                           │              │
│                                └───────────────┬───────────┘              │
│                                                ▼                          │
│                                    ┌─────────────────────┐                │
│                                    │ Scoring Layer       │                │
│                                    │ (Trust Score)       │                │
│                                    └─────────────────────┘                │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Registry Service (NestJS)
Standalone microservice based on UNDP National Carbon Registry.

**Location:** `/registry-service`

**Features:**
- Programme/Project lifecycle management
- Credit issuance, transfer, retirement
- Company and user management
- TypeORM entities for PostgreSQL

### 2. Integration Layer (FastAPI)
Bridge connecting CarbonCheck with Registry Service.

**Location:** `/integration-layer`

**Features:**
- REST API endpoints for registry operations
- Data mapping (Programme ↔ Project)
- Verification pipeline orchestration
- Trust score computation

### 3. Database Extensions
MRV tables for verification tracking.

**Location:** `/integration-layer/migrations`

**Tables:**
- `verification_results` - Stores verification outcomes
- `projects_extended` - Extended project data from registry
- `registry_sync_log` - Sync operation tracking

---

## Setup Instructions

### Prerequisites

- Node.js 18+
- Python 3.10+
- PostgreSQL 14+
- Docker (optional)

### Step 1: Registry Service Setup

```bash
cd registry-service

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Create database
createdb carbon_registry

# Start service
npm run start:dev
```

The registry service runs on `http://localhost:3001`

### Step 2: Integration Layer Setup

```bash
cd integration-layer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start service
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The integration layer runs on `http://localhost:8000`

### Step 3: Database Migration

Run the MRV extension migrations on your Supabase/PostgreSQL:

```bash
# Using psql
psql -h your-host -U your-user -d your-db -f migrations/001_mrv_extension.sql
psql -h your-host -U your-user -d your-db -f migrations/002_mrv_indexes.sql

# Or via Supabase SQL Editor - paste the SQL content
```

---

## API Endpoints

### Registry Integration API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/registry/projects` | List projects with filters |
| GET | `/api/registry/projects/{id}` | Get project by ID |
| POST | `/api/registry/projects` | Create new project |
| POST | `/api/registry/projects/{id}/verify` | Run verification pipeline |
| POST | `/api/registry/projects/{id}/authorize` | Authorize project |
| POST | `/api/registry/projects/{id}/issue-credits` | Issue credits |
| POST | `/api/registry/projects/{id}/transfer-credits` | Transfer credits |
| POST | `/api/registry/projects/{id}/retire-credits` | Retire credits |
| GET | `/api/registry/statistics` | Get registry statistics |
| GET | `/api/registry/leaderboard` | Get project leaderboard |
| GET | `/api/registry/health` | Health check |

### Example: Verify a Project

```bash
curl -X POST "http://localhost:8000/api/registry/projects/PRG-12345/verify?include_satellite=true&include_ai=true"
```

Response:
```json
{
  "project_id": "PRG-12345",
  "predicted_co2": 15420.5,
  "claimed_co2": 15000.0,
  "ndvi_avg": 0.65,
  "ndvi_change": 0.05,
  "anomaly_score": 0.028,
  "trust_score": 0.872,
  "confidence_interval": [13107.43, 17733.58],
  "verdict": "VERIFIED",
  "verification_timestamp": "2024-01-15T10:30:00Z",
  "data_sources": ["registry", "satellite_ndvi", "ai_model"]
}
```

---

## Data Mapping

### UNDP Programme → CarbonCheck Project

| UNDP Field | CarbonCheck Field |
|------------|-------------------|
| `programmeId` | `project_id` |
| `title` | `name` |
| `creditEst` | `claimed_co2` |
| `sector` | `methodology` |
| `geographicalLocationCordintes` | `region`, `location_coordinates` |
| `currentStage` | `status` |
| `emissionReductionAchieved` | `verified_co2` |
| `creditIssued` | `credits_issued` |
| `creditBalance` | `credits_balance` |

### Stage Mapping

| UNDP Stage | CarbonCheck Status |
|------------|-------------------|
| AwaitingAuthorization | pending |
| Pending | pending |
| Authorised | authorized |
| Rejected | rejected |
| CreditIssued | active |
| CreditTransferred | active |
| CreditRetired | completed |

---

## Docker Deployment

### docker-compose.yml

```yaml
version: '3.8'

services:
  registry-service:
    build: ./registry-service
    ports:
      - "3001:3001"
    environment:
      - REGISTRY_DB_HOST=db
      - REGISTRY_DB_PORT=5432
      - REGISTRY_DB_USER=postgres
      - REGISTRY_DB_PASSWORD=${DB_PASSWORD}
      - REGISTRY_DB_NAME=carbon_registry
    depends_on:
      - db

  integration-layer:
    build: ./integration-layer
    ports:
      - "8000:8000"
    environment:
      - REGISTRY_SERVICE_URL=http://registry-service:3001
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
    depends_on:
      - registry-service

  db:
    image: postgres:14
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=carbon_registry
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

Start with:
```bash
docker-compose up -d
```

---

## Verification Pipeline

The verification pipeline runs in 4 layers:

### 1. Ground Layer
- Fetches project data from UNDP Registry
- Maps Programme → Project format
- Extracts claimed CO2 and location data

### 2. Satellite Layer
- Connects to Google Earth Engine (optional)
- Retrieves NDVI time series data
- Calculates vegetation change metrics

### 3. AI Layer
- Runs CO2 prediction model
- Computes anomaly detection score
- Generates confidence intervals

### 4. Scoring Layer
- Combines all layer outputs
- Calculates final trust score
- Determines verdict (VERIFIED/FLAGGED/REJECTED)

---

## Extending the System

### Adding New Data Sources

1. Create service in `/integration-layer/app/services/`
2. Add to verification pipeline in `verification_service.py`
3. Update data sources in verification result

### Custom Scoring Logic

Modify `VerificationMapper.compute_verdict()` in `/integration-layer/app/mappers/programme_mapper.py`

### Adding New Endpoints

1. Add route in `/integration-layer/app/routers/registry_router.py`
2. Create corresponding service method
3. Update API documentation

---

## Troubleshooting

### Registry Service Not Connecting

```bash
# Check if service is running
curl http://localhost:3001/api/v1/programmes?size=1

# Check logs
cd registry-service && npm run start:dev
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql -h localhost -U postgres -d carbon_registry

# Check TypeORM sync
# Set synchronize: true in registry-service config
```

### Integration Layer Errors

```bash
# Check health
curl http://localhost:8000/api/registry/health

# Enable debug logging
LOG_LEVEL=DEBUG uvicorn app.main:app --reload
```

---

## File Structure

```
carboncheck/
├── registry-service/           # UNDP Registry (NestJS)
│   ├── src/
│   │   ├── entities/          # TypeORM entities
│   │   ├── services/          # Business logic
│   │   ├── controllers/       # API controllers
│   │   ├── dto/               # Data transfer objects
│   │   ├── enums/             # Enumerations
│   │   ├── config/            # Configuration
│   │   ├── app.module.ts      # Main module
│   │   └── main.ts            # Entry point
│   ├── package.json
│   └── tsconfig.json
│
├── integration-layer/          # FastAPI Bridge
│   ├── app/
│   │   ├── models/            # Pydantic models
│   │   ├── services/          # Service clients
│   │   ├── mappers/           # Data mappers
│   │   ├── routers/           # API routers
│   │   ├── config.py          # Configuration
│   │   └── main.py            # Entry point
│   ├── migrations/            # SQL migrations
│   └── requirements.txt
│
└── README.md                   # This file
```

---

## License

MIT License - See LICENSE file for details.

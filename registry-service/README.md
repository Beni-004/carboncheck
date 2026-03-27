# UNDP National Carbon Registry Service

NestJS service for managing the national carbon registry with PostgreSQL database.

## Features

- **Programme Management**: CRUD operations for carbon reduction programmes
- **Credit Tracking**: Issuance, transfer, and retirement of carbon credits
- **Transaction History**: Complete audit trail of all credit movements
- **RESTful API**: Comprehensive API for registry operations
- **Type-Safe**: Full TypeScript with validation
- **Database ORM**: TypeORM for PostgreSQL

## Tech Stack

- **Framework**: NestJS
- **Database**: PostgreSQL with TypeORM
- **Validation**: class-validator
- **Language**: TypeScript
- **Runtime**: Node.js 18+

## Getting Started

### Local Development

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your database configuration

# Run database migrations
npm run migration:run

# Start development server
npm run start:dev
```

Visit http://localhost:3001/api/v1/programmes for the API.

### Environment Variables

See `.env.example` for all available configuration options.

**Required:**
- `REGISTRY_DB_HOST`: PostgreSQL host
- `REGISTRY_DB_PORT`: PostgreSQL port (default: 5432)
- `REGISTRY_DB_USER`: Database user
- `REGISTRY_DB_PASSWORD`: Database password
- `REGISTRY_DB_NAME`: Database name

**Optional:**
- `REGISTRY_PORT`: Server port (default: 3001)
- `NODE_ENV`: Environment (development/production)
- `SYSTEM_COUNTRY`: Country code (default: NG)
- `SYSTEM_COUNTRY_NAME`: Country name (default: Nigeria)
- `DEFAULT_CREDIT_UNIT`: Credit unit (default: tCO2e)

## API Endpoints

### Programmes
- `GET /api/v1/programmes` - List all programmes
- `GET /api/v1/programmes/:id` - Get programme details
- `POST /api/v1/programmes` - Create new programme
- `PATCH /api/v1/programmes/:id` - Update programme
- `DELETE /api/v1/programmes/:id` - Delete programme

### Credits
- `GET /api/v1/credits` - List all credits
- `GET /api/v1/credits/:id` - Get credit details
- `POST /api/v1/credits/issue` - Issue new credits
- `POST /api/v1/credits/transfer` - Transfer credits
- `POST /api/v1/credits/retire` - Retire credits

### Transactions
- `GET /api/v1/transactions` - List all transactions
- `GET /api/v1/transactions/:id` - Get transaction details

## Production Deployment (Railway)

### Prerequisites
1. Railway account ([railway.app](https://railway.app))
2. Railway PostgreSQL database (or external PostgreSQL)

### Deployment Steps

#### 1. Create Railway Project
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

#### 2. Add PostgreSQL Database
```bash
# Via Railway Dashboard
# - In your project, click "New"
# - Select "Database" → "Add PostgreSQL"

# Or via Railway CLI
railway add --database postgresql
```

#### 3. Configure Root Directory
In Railway project settings:
- **Root Directory**: `registry-service`
- **Build Command**: (leave empty - Docker will handle it)
- **Start Command**: (leave empty - Dockerfile CMD will be used)

#### 4. Set Environment Variables
In Railway Dashboard → Variables tab:

**If using Railway PostgreSQL (recommended):**
```bash
REGISTRY_DB_HOST=${{Postgres.PGHOST}}
REGISTRY_DB_PORT=${{Postgres.PGPORT}}
REGISTRY_DB_USER=${{Postgres.PGUSER}}
REGISTRY_DB_PASSWORD=${{Postgres.PGPASSWORD}}
REGISTRY_DB_NAME=${{Postgres.PGDATABASE}}
NODE_ENV=production
SYSTEM_COUNTRY=NG
SYSTEM_COUNTRY_NAME=Nigeria
```

**If using external PostgreSQL:**
```bash
REGISTRY_DB_HOST=your-db-host.com
REGISTRY_DB_PORT=5432
REGISTRY_DB_USER=your-db-user
REGISTRY_DB_PASSWORD=your-db-password
REGISTRY_DB_NAME=carbon_registry
NODE_ENV=production
```

**Important Notes:**
- Railway automatically sets `PORT` - do not override it
- Use Railway's `${{Postgres.VARIABLE}}` syntax to reference Railway PostgreSQL
- Database is created automatically by TypeORM on first run (when `synchronize: true`)
- Set `NODE_ENV=production` to disable auto-synchronization
- Never commit database credentials to the repository

#### 5. Database Setup

**Option A: Auto-sync (for development)**
- TypeORM will automatically create tables on first run
- Enabled when `NODE_ENV != production`

**Option B: Migrations (for production)**
```bash
# Generate migration
npm run migration:generate -- -n InitialSchema

# Run migrations via Railway shell
railway run npm run migration:run
```

#### 6. Deploy
```bash
# Automatic deployment via Git push
git push origin main

# Or via Railway CLI
railway up

# Or redeploy from Railway dashboard
```

### Post-Deployment Verification

#### 1. Check Service Health
```bash
curl https://your-registry.railway.app/api/v1/health
```

Expected response:
```json
{
  "status": "ok",
  "info": {
    "database": {"status": "up"}
  }
}
```

#### 2. List Programmes
```bash
curl https://your-registry.railway.app/api/v1/programmes
```

#### 3. Create Test Programme
```bash
curl -X POST https://your-registry.railway.app/api/v1/programmes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Solar Energy Project",
    "description": "100MW solar farm",
    "location": "Lagos, Nigeria",
    "category": "Renewable Energy",
    "status": "Active"
  }'
```

#### 4. Check Logs
```bash
# Via Railway CLI
railway logs

# Or view in Railway Dashboard → Deployments tab
```

### Troubleshooting

**Issue: Database connection fails**
- Verify all `REGISTRY_DB_*` variables are set correctly
- If using Railway PostgreSQL, check that Postgres service is running
- Verify database credentials are correct
- Check Railway logs for specific connection errors

**Issue: Tables not created**
- Ensure `NODE_ENV=development` for auto-sync, OR
- Run migrations manually: `railway run npm run migration:run`
- Check that database user has CREATE TABLE permissions

**Issue: Build fails**
- Verify `package.json` has all required dependencies
- Check that TypeScript compiles locally: `npm run build`
- Review Railway build logs for specific errors

**Issue: Port binding error**
- Do NOT set `PORT` or `REGISTRY_PORT` in Railway
- Railway automatically sets `PORT` environment variable
- The app is configured to read `PORT` first, then fall back to `REGISTRY_PORT`

### Monitoring
- Use Railway's built-in metrics dashboard
- Monitor database connections and query performance
- Set up health check monitoring (UptimeRobot, etc.)
- Review Railway logs for errors and warnings

### Database Backups
Railway PostgreSQL includes:
- Automatic daily backups (retained for 7 days)
- Manual backup creation via dashboard
- Point-in-time recovery

For critical data:
1. Set up additional backup automation
2. Export data regularly via pg_dump
3. Store backups in external storage (S3, etc.)

## Development

### Project Structure
```
registry-service/
├── src/
│   ├── main.ts              # Application entry point
│   ├── app.module.ts        # Root module
│   ├── config/
│   │   └── configuration.ts # Configuration loader
│   ├── programmes/          # Programmes module
│   │   ├── programme.entity.ts
│   │   ├── programme.service.ts
│   │   └── programme.controller.ts
│   ├── credits/             # Credits module
│   └── transactions/        # Transactions module
├── package.json             # Node dependencies
├── Dockerfile              # Production container
└── .dockerignore           # Docker build exclusions
```

### Running Tests
```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Test coverage
npm run test:cov
```

### Database Migrations
```bash
# Generate migration from entities
npm run migration:generate -- -n MigrationName

# Run migrations
npm run migration:run

# Revert last migration
npm run migration:revert
```

### Local Docker Build
```bash
# Build image
docker build -t registry-service .

# Run container
docker run -p 3001:3000 \
  -e REGISTRY_DB_HOST=host.docker.internal \
  -e REGISTRY_DB_USER=postgres \
  -e REGISTRY_DB_PASSWORD=password \
  -e REGISTRY_DB_NAME=carbon_registry \
  registry-service
```

## API Documentation

### Create Programme
```bash
POST /api/v1/programmes
Content-Type: application/json

{
  "name": "Reforestation Project",
  "description": "Plant 10,000 trees",
  "location": "Abuja, Nigeria",
  "category": "Forestry",
  "status": "Active",
  "startDate": "2026-01-01",
  "estimatedCredits": 50000
}
```

### Issue Credits
```bash
POST /api/v1/credits/issue
Content-Type: application/json

{
  "programmeId": 1,
  "amount": 1000,
  "vintageYear": 2026,
  "serialNumberPrefix": "NG-RF-2026"
}
```

### Transfer Credits
```bash
POST /api/v1/credits/transfer
Content-Type: application/json

{
  "creditId": "NG-RF-2026-0001",
  "fromHolder": "Project Owner",
  "toHolder": "Buyer Corp",
  "amount": 100,
  "reason": "Sale"
}
```

### Retire Credits
```bash
POST /api/v1/credits/retire
Content-Type: application/json

{
  "creditId": "NG-RF-2026-0001",
  "amount": 50,
  "reason": "Offset emissions",
  "retiredBy": "Company ABC"
}
```

## License

MIT

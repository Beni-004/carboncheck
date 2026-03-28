# CarbonCheck Frontend

Next.js 14 frontend application for carbon credit verification and fraud detection.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Icons**: Lucide React
- **Language**: TypeScript

## Getting Started

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## Features

### User Story 1: Single Credit Verification
- `/verify` - Verify individual carbon credits
- Real-time trust score calculation with 4-check breakdown
- Color-coded verdict badges (PASS/WARNING/FAIL)
- Data provenance and fallback indicators

### User Story 2: Bulk Credit Audit
- `/verify/bulk` - Upload and verify up to 50 credits at once
- Ranked fraud report (worst credits first)
- CSV export functionality
- Per-item error handling

### User Story 3: Public Leaderboard
- `/leaderboard` - Public "Hall of Shame" for most-flagged credits
- Category filtering (Renewable Energy, Forestry, etc.)
- No login required
- Real-time flag count updates

## Environment Variables

```bash
# Optional: Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# If not set, the app uses mock data automatically
```

## Project Structure

```
apps/web/
├── app/
│   ├── layout.tsx          # Root layout with NavBar
│   ├── page.tsx            # Landing page
│   ├── verify/
│   │   ├── page.tsx        # Single verify
│   │   └── bulk/
│   │       └── page.tsx    # Bulk verify
│   └── leaderboard/
│       └── page.tsx        # Public leaderboard
├── components/
│   ├── ui/                 # shadcn/ui primitives
│   ├── trust-score-card.tsx
│   ├── trust-score-ring.tsx
│   ├── verdict-badge.tsx
│   ├── fraud-risk-list.tsx
│   ├── provenance-badges.tsx
│   ├── bulk-fraud-report-table.tsx
│   ├── leaderboard-table.tsx
│   └── nav-bar.tsx
└── lib/
    ├── api.ts              # API client with fallback
    ├── mock.ts             # Mock data generator
    └── utils.ts            # Utility functions
```

## Mock Data

The application works 100% offline with mock data. Three predefined examples:

- `VCS-2024-001` - PASS (score: 92)
- `GOLD-2023-556` - WARNING (score: 58)
- `ACR-2021-999` - FAIL (score: 15)

Any other ID generates random realistic data.

## Design System

### Trust Score Ring
- **Red (0-40)**: FAIL - High fraud risk
- **Amber (41-70)**: WARNING - Medium risk
- **Green (71-100)**: PASS - Low risk

### Verdict Badges
- Uppercase styling (FAIL/WARNING/PASS)
- Color-coded backgrounds with borders
- Consistent sizing (sm/md/lg)

### Dark Mode
Default dark theme optimized for B2B compliance tools.

## API Integration

When `NEXT_PUBLIC_API_URL` is set, the frontend automatically:
1. Attempts to call the backend API
2. Falls back to mock data on timeout/error
3. Displays data provenance badges

All API calls have automatic fallback - the demo never breaks.

## Development

### Adding New Components

```bash
# Install shadcn components
npx shadcn-ui@latest add [component-name]
```

### Type Safety

All API responses use TypeScript interfaces defined in `lib/mock.ts`:
- `TrustScoreResult`
- `BulkVerifyResult`
- `LeaderboardEntry`

## Production Deployment (Vercel)

### Prerequisites
1. A Vercel account ([vercel.com](https://vercel.com))
2. Backend services deployed on Railway (see `backend/README.md`)

### Deployment Steps

#### 1. Connect Repository to Vercel
- Import your repository in Vercel dashboard
- Select **monorepo** setup

#### 2. Configure Root Directory
In Vercel project settings:
- **Framework Preset**: Next.js
- **Root Directory**: `apps/web`
- **Build Command**: `npm run build` (auto-detected)
- **Install Command**: `npm install` (auto-detected)
- **Output Directory**: `.next` (auto-detected)

#### 3. Set Environment Variables
In Vercel Dashboard → Settings → Environment Variables:

**Required:**
```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

**Optional (for full integration):**
```bash
NEXT_PUBLIC_INTEGRATION_API_URL=https://your-integration-layer.railway.app
NEXT_PUBLIC_REGISTRY_API_URL=https://your-registry-service.railway.app
```

**Important Notes:**
- All `NEXT_PUBLIC_*` variables are exposed to the browser
- Never put secrets in `NEXT_PUBLIC_*` variables
- The app works with mock data if `NEXT_PUBLIC_API_URL` is not set
- Set variables for all environments (Production, Preview, Development)

#### 4. Deploy
```bash
# Deploy via Git (automatic)
git push origin main

# Or deploy via Vercel CLI
npx vercel
```

### Verification
After deployment:
1. Visit your Vercel URL (e.g., `https://carboncheck.vercel.app`)
2. Test the `/verify` page with a credit ID
3. Check browser console for API connection status
4. Verify data provenance badges show "Live API" when backend is connected

### Troubleshooting

**Issue: Frontend shows mock data instead of real API data**
- Check that `NEXT_PUBLIC_API_URL` is set in Vercel
- Verify backend is accessible (check Railway logs)
- Check browser console for CORS or network errors

**Issue: Build fails on Vercel**
- Ensure `package.json` has all required dependencies
- Check that TypeScript compiles locally: `npm run build`
- Review Vercel build logs for specific errors

**Issue: Environment variables not working**
- Redeploy after adding environment variables
- Ensure variable names start with `NEXT_PUBLIC_`
- Check that variables are set for the correct environment (Production/Preview)

### Performance Optimization
- Next.js automatically optimizes images and fonts
- API calls include timeout and error handling
- Client-side caching for leaderboard data
- Automatic code splitting per route

### Monitoring
- Use Vercel Analytics for performance metrics
- Check Vercel Logs for runtime errors
- Monitor backend API health at `https://your-backend.railway.app/health`

## License

MIT

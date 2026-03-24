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

## License

MIT

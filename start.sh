#!/bin/bash
# Quick start script for CarbonCheck

echo "===================================================================="
echo "                   CARBONCHECK QUICK START"
echo "===================================================================="
echo ""

# Check if database migration has been run
echo "Step 1: Checking database setup..."
cd backend
if ./venv/bin/python test_db_connection.py 2>&1 | grep -q "✓.*table exists"; then
    echo "✅ Database tables found!"
else
    echo "❌ Database tables not found!"
    echo ""
    echo "Please run the database migration first:"
    echo "1. Open: https://supabase.com/dashboard/project/oyevylxqjeokjfsuacau/sql/new"
    echo "2. Copy SQL from: backend/supabase_local/migrations/20260324_001_init_carboncheck.sql"
    echo "3. Paste and click 'Run'"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo ""
echo "Step 2: Checking environment files..."

# Check backend .env
if [ -f "backend/.env" ] && grep -q "SUPABASE_URL" backend/.env; then
    echo "✅ Backend .env configured"
else
    echo "❌ Backend .env missing or incomplete"
    exit 1
fi

# Check frontend .env.local
if [ -f "apps/web/.env.local" ] && grep -q "NEXT_PUBLIC_API_URL" apps/web/.env.local; then
    echo "✅ Frontend .env.local configured"
else
    echo "❌ Frontend .env.local missing"
    echo "Creating it now..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > apps/web/.env.local
    echo "✅ Created apps/web/.env.local"
fi

cd ..

echo ""
echo "===================================================================="
echo "                   READY TO START!"
echo "===================================================================="
echo ""
echo "Open TWO terminal windows and run:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd apps/web"
echo "  npm install  # (first time only)"
echo "  npm run dev"
echo ""
echo "Then open: http://localhost:3000"
echo ""
echo "===================================================================="

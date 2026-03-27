#!/bin/bash
# Automated startup script for CarbonCheck - runs both backend and frontend

set -e  # Exit on error

echo "===================================================================="
echo "                   CARBONCHECK AUTOMATED STARTUP"
echo "===================================================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Cleanup function to kill background processes
cleanup() {
    echo ""
    echo "===================================================================="
    print_info "Shutting down servers..."
    echo "===================================================================="
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        print_info "Backend server stopped (PID: $BACKEND_PID)"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_info "Frontend server stopped (PID: $FRONTEND_PID)"
    fi
    
    exit 0
}

# Trap SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

# Step 1: Check Python virtual environment
echo "Step 1: Checking Python virtual environment..."
if [ ! -d "backend/venv" ]; then
    print_error "Python virtual environment not found!"
    print_info "Creating virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
    print_success "Virtual environment created"
else
    print_success "Virtual environment found"
fi

# Step 2: Install Python dependencies
echo ""
echo "Step 2: Installing Python dependencies..."
cd backend
if ! source venv/bin/activate 2>/dev/null; then
    print_error "Failed to activate virtual environment"
    print_info "Try running: cd backend && source venv/bin/activate"
    exit 1
fi

print_info "Installing requirements.txt..."
pip install -q -r requirements.txt
print_success "Python dependencies installed"

# Step 3: Check database connection
echo ""
echo "Step 3: Checking database connection..."
if python test_db_connection.py 2>&1 | grep -q "health check passed"; then
    print_success "Database tables found!"
else
    print_error "Database tables not found!"
    echo ""
    print_info "Please run the database migration first:"
    echo "1. Open: https://supabase.com/dashboard/project/oyevylxqjeokjfsuacau/sql/new"
    echo "2. Copy SQL from: backend/supabase_local/migrations/20260324_001_init_carboncheck.sql"
    echo "3. Paste and click 'Run'"
    echo ""
    print_info "Then run this script again."
    exit 1
fi

cd ..

# Step 4: Check backend .env
echo ""
echo "Step 4: Checking backend environment configuration..."
if [ -f "backend/.env" ] && grep -q "SUPABASE_URL" backend/.env; then
    print_success "Backend .env configured"
else
    print_error "Backend .env missing or incomplete"
    exit 1
fi

# Step 5: Setup frontend environment
echo ""
echo "Step 5: Setting up frontend environment..."
if [ ! -f "apps/web/.env.local" ]; then
    print_info "Creating apps/web/.env.local..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > apps/web/.env.local
    print_success "Created apps/web/.env.local"
else
    print_success "Frontend .env.local exists"
fi

# Step 6: Install frontend dependencies
echo ""
echo "Step 6: Installing frontend dependencies..."
cd apps/web
if [ ! -d "node_modules" ]; then
    print_info "Installing npm packages (this may take a minute)..."
    npm install
    print_success "Frontend dependencies installed"
else
    print_success "Frontend dependencies already installed"
fi
cd ../..

# Step 7: Start backend server
echo ""
echo "===================================================================="
echo "Step 7: Starting Backend Server (FastAPI)"
echo "===================================================================="
cd backend
source venv/bin/activate

print_info "Starting backend on http://localhost:8000..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!

# Wait a moment and check if backend started
sleep 3
if kill -0 $BACKEND_PID 2>/dev/null; then
    print_success "Backend server started (PID: $BACKEND_PID)"
    print_info "Backend logs: backend.log"
    print_info "Backend API: http://localhost:8000"
    print_info "API Docs: http://localhost:8000/docs"
else
    print_error "Backend failed to start!"
    print_info "Check backend.log for errors"
    cat ../backend.log
    exit 1
fi

cd ..

# Step 8: Start frontend server
echo ""
echo "===================================================================="
echo "Step 8: Starting Frontend Server (Next.js)"
echo "===================================================================="
cd apps/web

print_info "Starting frontend on http://localhost:3000..."
npm run dev > ../../frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait a moment and check if frontend started
sleep 5
if kill -0 $FRONTEND_PID 2>/dev/null; then
    print_success "Frontend server started (PID: $FRONTEND_PID)"
    print_info "Frontend logs: frontend.log"
else
    print_error "Frontend failed to start!"
    print_info "Check frontend.log for errors"
    cat ../../frontend.log
    cleanup
    exit 1
fi

cd ../..

# All done!
echo ""
echo "===================================================================="
echo "                   ✓ ALL SERVERS RUNNING!"
echo "===================================================================="
echo ""
echo "  🌐 Frontend:  http://localhost:3000"
echo "  🔌 Backend:   http://localhost:8000"
echo "  📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "  📋 Backend logs:  tail -f backend.log"
echo "  📋 Frontend logs: tail -f frontend.log"
echo ""
echo "  Press Ctrl+C to stop all servers"
echo "===================================================================="
echo ""

# Keep script running and monitor processes
while true; do
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        print_error "Backend server died unexpectedly!"
        print_info "Check backend.log for errors"
        cleanup
        exit 1
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        print_error "Frontend server died unexpectedly!"
        print_info "Check frontend.log for errors"
        cleanup
        exit 1
    fi
    
    sleep 5
done

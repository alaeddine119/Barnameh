#!/bin/bash

# Frontend Integration Quick Start
# This script helps you test the ML Dashboard

set -e

echo "🚀 Frontend Integration Quick Start"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check ML API
echo "📡 Step 1: Checking ML API..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ ML API is running${NC}"
else
    echo -e "${YELLOW}⚠ ML API is not running${NC}"
    echo "  Start it with:"
    echo "    cd packages/ml-engine"
    echo "    source venv/bin/activate"
    echo "    python -m api.main"
    echo ""
fi

# Step 2: Check Database
echo ""
echo "🗄️  Step 2: Checking Database..."
if docker ps | grep postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Database is running${NC}"
else
    echo -e "${YELLOW}⚠ Database is not running${NC}"
    echo "  Start it with:"
    echo "    cd packages/database"
    echo "    docker compose up -d"
    echo ""
fi

# Step 3: Check Dependencies
echo ""
echo "📦 Step 3: Checking Frontend Dependencies..."
cd "$(dirname "$0")"
if [ -d "node_modules/recharts" ]; then
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠ Installing dependencies...${NC}"
    bun install recharts
fi

# Step 4: Environment Variables
echo ""
echo "🔧 Step 4: Checking Environment Variables..."
if [ -f ".env.local" ]; then
    echo -e "${GREEN}✓ .env.local exists${NC}"
else
    echo -e "${YELLOW}⚠ Creating .env.local...${NC}"
    cat > .env.local << EOF
# ML API Configuration
NEXT_PUBLIC_ML_API_URL=http://localhost:8000/api/v1

# Demo Organization (from seed data)
NEXT_PUBLIC_DEMO_ORG_ID=11111111-1111-1111-1111-111111111111
EOF
    echo -e "${GREEN}✓ Created .env.local${NC}"
fi

# Step 5: Test API Connection
echo ""
echo "🧪 Step 5: Testing API Connection..."
if curl -s http://localhost:8000/api/v1/kpi/summary?organization_id=11111111-1111-1111-1111-111111111111 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API responding with data${NC}"
else
    echo -e "${RED}✗ API not responding${NC}"
    echo "  Make sure:"
    echo "    1. Database is running (docker compose up -d)"
    echo "    2. Database is seeded (./setup.sh in database folder)"
    echo "    3. ML API is running (python -m api.main)"
    echo ""
fi

# Summary
echo ""
echo "📊 Dashboard Information"
echo "========================"
echo "Dashboard URL: http://localhost:3001/ml-dashboard"
echo "ML API URL:    http://localhost:8000"
echo "pgAdmin URL:   http://localhost:5050"
echo ""
echo "Demo IDs:"
echo "  Organization: 11111111-1111-1111-1111-111111111111"
echo "  Product A:    PROD-A-001"
echo "  Product B:    PROD-B-002"
echo ""

# Final instructions
echo "🎯 Next Steps:"
echo "=============="
echo "1. Start the development server:"
echo "   npm run dev"
echo ""
echo "2. Open your browser:"
echo "   http://localhost:3001/ml-dashboard"
echo ""
echo "3. You should see:"
echo "   ✓ KPI Dashboard with real-time metrics"
echo "   ✓ Demand Forecast charts for Products A & B"
echo "   ✓ Anomaly Alerts with severity indicators"
echo ""
echo "📚 Documentation:"
echo "   - Frontend Integration: ./FRONTEND_INTEGRATION.md"
echo "   - ML Engine: ../../packages/ml-engine/README.md"
echo "   - Database: ../../packages/database/README.md"
echo ""
echo -e "${GREEN}✨ Ready to start!${NC}"

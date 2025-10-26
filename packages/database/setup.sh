#!/bin/bash

# Smart Operations Platform - Database Setup Script
# This script sets up the complete database environment

set -e  # Exit on error

echo "🚀 Smart Operations Platform - Database Setup"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed (v1 or v2)
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose found${NC}"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}📝 Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ .env file created${NC}"
else
    echo -e "${YELLOW}ℹ️  .env file already exists${NC}"
fi
echo ""

# Stop existing containers if running
echo -e "${YELLOW}🛑 Stopping existing containers (if any)...${NC}"
$DOCKER_COMPOSE down 2>/dev/null || true
echo ""

# Start services
echo -e "${YELLOW}🐳 Starting database services...${NC}"
$DOCKER_COMPOSE up -d

# Wait for PostgreSQL to be ready
echo -e "${YELLOW}⏳ Waiting for PostgreSQL to be ready...${NC}"
sleep 5

# Check if PostgreSQL is ready
MAX_RETRIES=30
RETRY_COUNT=0
while ! $DOCKER_COMPOSE exec -T postgres pg_isready -U barnameh_user -d barnameh_ops > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT+1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo -e "${RED}❌ PostgreSQL failed to start within expected time${NC}"
        echo "   Check logs with: docker-compose logs postgres"
        exit 1
    fi
    echo -n "."
    sleep 1
done

echo ""
echo -e "${GREEN}✅ PostgreSQL is ready!${NC}"
echo ""

# Check if Python is installed
if command -v python3 &> /dev/null; then
    echo -e "${YELLOW}🐍 Installing Python dependencies...${NC}"
    if [ -f requirements.txt ]; then
        python3 -m pip install -q -r requirements.txt 2>/dev/null || {
            echo -e "${YELLOW}⚠️  Could not install Python dependencies automatically${NC}"
            echo "   Please run: pip install -r requirements.txt"
        }
    fi
    echo ""
else
    echo -e "${YELLOW}⚠️  Python3 not found. Skipping Python dependency installation.${NC}"
    echo "   Install Python3 to use the Python utilities."
    echo ""
fi

# Display status
echo -e "${GREEN}✨ Setup Complete!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}📊 Database Information${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PostgreSQL:  postgresql://localhost:5432/barnameh_ops"
echo "Username:    barnameh_user"
echo "Password:    barnameh_password"
echo ""
echo -e "${GREEN}🔧 Services${NC}"
echo "pgAdmin:     http://localhost:5050"
echo "  Email:     admin@barnameh.local"
echo "  Password:  admin"
echo ""
echo "Redis:       redis://localhost:6379"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}📝 Sample Data${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
$DOCKER_COMPOSE exec -T postgres psql -U barnameh_user -d barnameh_ops -c "
SELECT 
    'Organizations' as entity, COUNT(*)::text as count FROM organizations
UNION ALL
SELECT 'Locations', COUNT(*)::text FROM locations
UNION ALL
SELECT 'Resources', COUNT(*)::text FROM resources
UNION ALL
SELECT 'Employees', COUNT(*)::text FROM employees
UNION ALL
SELECT 'Demand History', COUNT(*)::text FROM demand_history
UNION ALL
SELECT 'Operational Events', COUNT(*)::text FROM operational_events
UNION ALL
SELECT 'Forecasts', COUNT(*)::text FROM demand_forecasts
UNION ALL
SELECT 'Anomaly Predictions', COUNT(*)::text FROM anomaly_predictions
" -t 2>/dev/null || echo "Could not fetch data summary"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🚀 Next Steps${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Access pgAdmin:    http://localhost:5050"
echo "2. Test Python utils: python3 db_utils.py"
echo "3. View logs:         $DOCKER_COMPOSE logs -f"
echo "4. Stop services:     $DOCKER_COMPOSE down"
echo "5. Read docs:         cat README.md"
echo ""
echo -e "${GREEN}✅ Happy hacking! 🎉${NC}"

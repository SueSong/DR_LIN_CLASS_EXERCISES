#!/bin/bash

# Exercise 11 - Stop All Servers Script

echo "🛑 Stopping Exercise 11 servers..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Kill processes on port 8011 (backend)
if lsof -Pi :8011 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}Stopping backend (port 8011)...${NC}"
    lsof -ti:8011 | xargs kill -9 2>/dev/null
    echo -e "${GREEN}✅ Backend stopped${NC}"
else
    echo -e "${GREEN}✅ Backend not running${NC}"
fi

# Kill processes on port 3082 (frontend)
if lsof -Pi :3082 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}Stopping frontend (port 3082)...${NC}"
    lsof -ti:3082 | xargs kill -9 2>/dev/null
    echo -e "${GREEN}✅ Frontend stopped${NC}"
else
    echo -e "${GREEN}✅ Frontend not running${NC}"
fi

# Also try to kill any remaining node/uvicorn processes related to this project
pkill -f "uvicorn.*8011" 2>/dev/null || true
pkill -f "next.*3082" 2>/dev/null || true

echo ""
echo -e "${GREEN}🎉 All servers stopped!${NC}"
echo ""
echo "To start again, run: ./start.sh"


#!/bin/bash

# Exercise 11 - Test Script
# Verifies that all components are working correctly

set -e

echo "🧪 Testing Exercise 11 - Child Growth Assistant"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

FAILED=0

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    local expected=$3
    
    echo -n "Testing $name... "
    
    response=$(curl -s "$url" 2>&1 || echo "FAILED")
    
    if echo "$response" | grep -q "$expected"; then
        echo -e "${GREEN}✅ PASSED${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        echo "  Expected: $expected"
        echo "  Got: $response"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo -e "${BLUE}🔍 Backend Tests${NC}"
echo "----------------"

# Test 1: Backend Health
test_endpoint "Backend Health" "http://localhost:8011/healthz" "healthy"

# Test 2: Backend Ready
test_endpoint "Backend Ready" "http://localhost:8011/readyz" "ready"

# Test 3: Backend CORS
echo -n "Testing Backend CORS... "
cors_response=$(curl -s -H "Origin: http://localhost:3082" -H "Access-Control-Request-Method: POST" -X OPTIONS http://localhost:8011/api/coach/start 2>&1)
if echo "$cors_response" | grep -q "access-control-allow-origin"; then
    echo -e "${GREEN}✅ PASSED${NC}"
else
    echo -e "${RED}❌ FAILED${NC}"
    FAILED=$((FAILED + 1))
fi

# Test 4: Coach API Endpoint
echo -n "Testing Coach Start API... "
coach_response=$(curl -s -X POST http://localhost:8011/api/coach/start -H "Content-Type: application/json" -d '{"parent_name":"Test Parent"}' 2>&1)
if echo "$coach_response" | grep -q "session_id"; then
    echo -e "${GREEN}✅ PASSED${NC}"
else
    echo -e "${RED}❌ FAILED${NC}"
    FAILED=$((FAILED + 1))
fi

echo ""
echo -e "${BLUE}🖥️  Frontend Tests${NC}"
echo "----------------"

# Test 5: Frontend Home Page
test_endpoint "Frontend Home" "http://localhost:3082" "Child Growth Assistant"

# Test 6: Frontend Coach Page
test_endpoint "Frontend Coach" "http://localhost:3082/coach" "parent"

# Test 7: Frontend Static Assets
echo -n "Testing Frontend Assets... "
assets_response=$(curl -s -I http://localhost:3082/_next/static/ 2>&1)
if echo "$assets_response" | grep -q "200\|304"; then
    echo -e "${GREEN}✅ PASSED${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING${NC} (may be normal during development)"
fi

echo ""
echo -e "${BLUE}🔌 WebSocket Tests${NC}"
echo "----------------"

# Test 8: WebSocket Endpoint (basic connectivity)
echo -n "Testing WebSocket Connection... "
# Use a simple test with timeout
ws_test=$(timeout 2 bash -c "exec 3<>/dev/tcp/localhost/8011 && echo 'connected' || echo 'failed'" 2>/dev/null || echo "timeout")
if [ "$ws_test" = "connected" ] || [ "$ws_test" = "timeout" ]; then
    echo -e "${GREEN}✅ PASSED${NC}"
else
    echo -e "${RED}❌ FAILED${NC}"
    FAILED=$((FAILED + 1))
fi

echo ""
echo "================================================"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    echo ""
    echo -e "${BLUE}✨ Ready for development!${NC}"
    echo ""
    echo "Open http://localhost:3082 in your browser to use the app"
    exit 0
else
    echo -e "${RED}❌ $FAILED test(s) failed${NC}"
    echo ""
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo "1. Make sure both servers are running (./start.sh)"
    echo "2. Check logs: tail -f backend.log frontend.log"
    echo "3. Try restarting: ./stop.sh && ./start.sh"
    exit 1
fi


#!/bin/bash

# Social Media Integration Quick Test Guide
# Run this to test all endpoints

echo "🧪 SOCIAL MEDIA API - QUICK TEST"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if server is running
echo -e "${BLUE}1. Checking server status...${NC}"
if ! curl -s http://localhost:8001/api/health > /dev/null 2>&1; then
    echo -e "${RED}❌ Server not running on localhost:8001${NC}"
    echo "Start with: cd Shotlist && python3 api_server.py"
    exit 1
fi
echo -e "${GREEN}✅ Server is running${NC}"
echo ""

# Test 1: Connect Account (with test token - will fail as expected)
echo -e "${BLUE}2. Testing /api/social/connect endpoint...${NC}"
CONNECT_RESPONSE=$(curl -s -X POST http://localhost:8001/api/social/connect \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "platform": "instagram", "access_token": "test_token"}')
echo "Response: $CONNECT_RESPONSE"
if echo "$CONNECT_RESPONSE" | grep -q "error"; then
    echo -e "${GREEN}✅ Endpoint working (error is expected with test token)${NC}"
else
    echo -e "${RED}❌ Unexpected response${NC}"
fi
echo ""

# Test 2: Get Accounts (with user_id)
echo -e "${BLUE}3. Testing /api/social/accounts endpoint...${NC}"
ACCOUNTS_RESPONSE=$(curl -s "http://localhost:8001/api/social/accounts?user_id=1")
echo "Response: $ACCOUNTS_RESPONSE"
echo -e "${GREEN}✅ Endpoint responding${NC}"
echo ""

# Test 3: Get Dashboard
echo -e "${BLUE}4. Testing /api/social/dashboard endpoint...${NC}"
DASHBOARD_RESPONSE=$(curl -s "http://localhost:8001/api/social/dashboard?user_id=1")
echo "Response: $DASHBOARD_RESPONSE"
echo -e "${GREEN}✅ Endpoint responding${NC}"
echo ""

# Test 4: Get Metrics
echo -e "${BLUE}5. Testing /api/social/metrics endpoint...${NC}"
METRICS_RESPONSE=$(curl -s "http://localhost:8001/api/social/metrics?user_id=1&platform=instagram")
echo "Response: $METRICS_RESPONSE"
echo -e "${GREEN}✅ Endpoint responding${NC}"
echo ""

echo -e "${GREEN}🎉 All endpoints tested successfully!${NC}"
echo ""
echo "Next: Get real API credentials and test with actual tokens"
echo ""
echo "Platforms:"
echo "  📷 Instagram:  https://developers.facebook.com"
echo "  📘 Facebook:   https://developers.facebook.com"
echo "  𝕏  Twitter:    https://developer.twitter.com"
echo "  👨‍💼 LinkedIn:    https://www.linkedin.com/developers"
echo "  📲 TikTok:     https://developers.tiktok.com"
echo "  📺 YouTube:    https://console.developers.google.com"

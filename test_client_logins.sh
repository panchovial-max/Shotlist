#!/bin/bash

clients=(
  "techstartup@example.com:demo123:Tech Startup Client"
  "ecommerce@example.com:demo123:E-commerce Client"
  "fashionbrand@example.com:demo123:Fashion Brand Client"
  "restaurant@example.com:demo123:Restaurant Client"
  "saascompany@example.com:demo123:SaaS Company Client"
)

echo "🧪 Testing All Client Logins..."
echo "================================"

for client in "${clients[@]}"; do
  IFS=':' read -r email password fullname <<< "$client"
  echo ""
  echo "Testing: $fullname ($email)"
  
  response=$(curl -s -X POST http://localhost:8001/api/login \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$email\",\"password\":\"$password\"}")
  
  success=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null)
  
  if [ "$success" = "True" ]; then
    session=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('session_id', 'N/A'))" 2>/dev/null)
    echo "✅ SUCCESS - Session: ${session:0:20}..."
  else
    error=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('message', 'Unknown error'))" 2>/dev/null)
    echo "❌ FAILED - $error"
  fi
done

echo ""
echo "================================"
echo "Testing Admin Account"
echo ""
response=$(curl -s -X POST http://localhost:8001/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@shotlist.com","password":"admin123"}')

success=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null)

if [ "$success" = "True" ]; then
  session=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('session_id', 'N/A'))" 2>/dev/null)
  echo "✅ Admin Login SUCCESS - Session: ${session:0:20}..."
else
  error=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('message', 'Unknown error'))" 2>/dev/null)
  echo "❌ Admin Login FAILED - $error"
fi


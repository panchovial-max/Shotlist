#!/bin/bash

# SHOTLIST Campaign Analytics Starter Script
# Starts both the website server and API server

echo "🎨 SHOTLIST CAMPAIGN ANALYTICS"
echo "=============================="
echo ""

# Check if database exists
if [ ! -f "shotlist_analytics.db" ]; then
    echo "⚠️  Database not found. Initializing..."
    python3 init_database.py
    echo ""
fi

# Check if API server is already running
if lsof -ti:8001 > /dev/null 2>&1; then
    echo "⚠️  API server already running on port 8001"
    echo "   Kill it with: kill $(lsof -ti:8001)"
    echo ""
else
    echo "🚀 Starting API server on port 8001..."
    python3 api_server.py > api_server.log 2>&1 &
    API_PID=$!
    echo "   API Server PID: $API_PID"
    echo ""
    sleep 2
fi

# Check if website server is already running
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "⚠️  Website server already running on port 8000"
    echo "   Kill it with: kill $(lsof -ti:8000)"
    echo ""
else
    echo "🚀 Starting website server on port 8000..."
    python3 -m http.server 8000 > website_server.log 2>&1 &
    WEB_PID=$!
    echo "   Website Server PID: $WEB_PID"
    echo ""
    sleep 1
fi

echo "=============================="
echo "✅ SERVERS RUNNING"
echo "=============================="
echo ""
echo "📊 Dashboard:  http://localhost:8000/dashboard.html"
echo "🌐 Website:    http://localhost:8000"
echo "📡 API:        http://localhost:8001/api"
echo ""
echo "=============================="
echo ""
echo "📝 Logs:"
echo "   API:     tail -f api_server.log"
echo "   Website: tail -f website_server.log"
echo ""
echo "⛔ To stop servers:"
echo "   kill \$(lsof -ti:8000 8001)"
echo ""

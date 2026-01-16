#!/bin/bash

echo "🚀 Starting SHOTLIST Server..."

# Kill any existing processes
killall python3 2>/dev/null
sleep 2

# Navigate to project directory
cd /Users/franciscovialbrown/Documents/GitHub/Shotlist

# Start API server
echo "Starting API server on port 8001..."
python3 api_server.py &

# Wait for server to start
sleep 3

# Check if server is running
if curl -s http://localhost:8001/api/health > /dev/null; then
    echo "✅ Server is running!"
    echo ""
    echo "📱 Access points:"
    echo "  Login:     http://localhost:8000/login.html"
    echo "  Dashboard: http://localhost:8000/dashboard.html"
    echo "  Settings:  http://localhost:8000/settings.html"
    echo ""
    echo "🔑 Test credentials:"
    echo "  Email:    techstartup@example.com"
    echo "  Password: demo123"
else
    echo "❌ Server failed to start. Check api_server.py for errors."
fi

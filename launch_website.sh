#!/bin/bash

# Shotlist Website Launcher
# Quick script to launch the website locally

echo "🎨 SHOTLIST WEBSITE LAUNCHER"
echo "=============================="
echo ""

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 detected"
    echo "🚀 Launching website on http://localhost:8000"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    python3 -m http.server 8000
    
# Check if Python 2 is available
elif command -v python &> /dev/null; then
    echo "✅ Python 2 detected"
    echo "🚀 Launching website on http://localhost:8000"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    python -m SimpleHTTPServer 8000
    
# Check if Node.js is available
elif command -v npx &> /dev/null; then
    echo "✅ Node.js detected"
    echo "🚀 Launching website on http://localhost:8000"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    npx http-server -p 8000
    
else
    echo "❌ No suitable server found"
    echo ""
    echo "Please install one of the following:"
    echo "  - Python 3: https://www.python.org/downloads/"
    echo "  - Node.js: https://nodejs.org/"
    echo ""
    echo "Or simply open index.html directly in your browser"
    
    # Try to open in default browser
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open index.html
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open index.html
    fi
fi


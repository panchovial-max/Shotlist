#!/bin/bash

# Figma Plugin Build Script
# Builds the Figma Localhost Sync Plugin using Bun

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║     🎨 FIGMA LOCALHOST SYNC PLUGIN - BUILD SCRIPT             ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Bun is installed
if ! command -v bun &> /dev/null; then
    echo "❌ Bun is not installed!"
    echo "📦 Installing Bun..."
    curl -fsSL https://bun.sh/install | bash
    export PATH="$HOME/.bun/bin:$PATH"
fi

echo "✅ Bun version: $(bun --version)"
echo ""

# Navigate to plugin directory
PLUGIN_DIR="/Users/franciscovialbrown/Documents/GitHub/Shotlist/figma-localhost-sync"

if [ ! -d "$PLUGIN_DIR" ]; then
    echo "❌ Plugin directory not found: $PLUGIN_DIR"
    exit 1
fi

cd "$PLUGIN_DIR"
echo "📂 Working directory: $(pwd)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
if [ ! -d "node_modules" ]; then
    bun install
else
    echo "✅ Dependencies already installed"
fi
echo ""

# Build code.ts
echo "🔨 Building code.ts..."
bun build code.ts --outfile=code.js
if [ -f "code.js" ]; then
    echo "✅ code.js built successfully"
else
    echo "❌ Failed to build code.js"
    exit 1
fi
echo ""

# Build ui.ts
echo "🔨 Building ui.ts..."
bun build ui.ts --outfile=ui.js
if [ -f "ui.js" ]; then
    echo "✅ ui.js built successfully"
else
    echo "❌ Failed to build ui.js"
    exit 1
fi
echo ""

# Verify manifest.json
echo "📋 Verifying manifest.json..."
if [ -f "manifest.json" ]; then
    echo "✅ manifest.json found"
    cat manifest.json | python3 -m json.tool > /dev/null && echo "✅ manifest.json is valid JSON" || echo "❌ manifest.json has JSON errors"
else
    echo "❌ manifest.json not found"
    exit 1
fi
echo ""

# List built files
echo "📁 Plugin files built:"
ls -lh code.js ui.js manifest.json 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
echo ""

# Instructions
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║              ✅ BUILD SUCCESSFUL!                             ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

echo "📦 Plugin is ready to import into Figma!"
echo ""

echo "🔧 NEXT STEPS:"
echo ""
echo "1. Open Figma Desktop App"
echo "2. Go to Plugins → Development → Import plugin from manifest..."
echo "3. Select: $PLUGIN_DIR/manifest.json"
echo "4. Plugin will load and appear in your Plugins menu"
echo ""

echo "💡 WATCH MODE (For Development):"
echo ""
echo "  # Terminal 1:"
echo "  cd $PLUGIN_DIR"
echo "  bun build code.ts --outfile=code.js --watch"
echo ""
echo "  # Terminal 2:"
echo "  cd $PLUGIN_DIR"
echo "  bun build ui.ts --outfile=ui.js --watch"
echo ""
echo "  Then reload plugin in Figma after changes"
echo ""

echo "📖 For full documentation, see: FIGMA_SYNC_GUIDE.md"
echo ""

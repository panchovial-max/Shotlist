#!/bin/bash

# Deploy Shotlist Website to Vercel
echo "🚀 DEPLOYING SHOTLIST TO VERCEL"
echo "================================"
echo ""

# Load token from .env
if [ -f .env ]; then
    export $(cat .env | grep VERCEL_TOKEN | xargs)
fi

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

# Deploy
echo "🌐 Deploying to Vercel..."
echo ""

vercel --token $VERCEL_TOKEN --prod

echo ""
echo "✅ Deployment complete!"
echo "🌍 Your site is now live!"


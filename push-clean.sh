#!/bin/bash
# Script to push with clean history (no secrets)

echo "🚀 Creating clean branch without secret in history..."

cd /Users/franciscovialbrown/Documents/GitHub/PVB-NEW-WEB

# Backup current branch
git branch main-backup

# Create new orphan branch (no history)
git checkout --orphan main-clean

# Add all files
git add .

# Create single clean commit
git commit -m "Deploy PVB Estudio Creativo website - Complete project

- Full website with all features (index, dashboard, settings, login)
- PVB branding and greyscale color palette
- WhatsApp integration and agenda calendar
- Social media and ads platform integrations
- GitHub Actions workflow for auto-deploy
- Netlify configuration
- All assets and documentation
- Security: No secrets in code (uses environment variables)"

# Replace main branch
git branch -D main
git branch -m main

# Force push (this will overwrite remote history)
echo ""
echo "⚠️  About to force push - this will overwrite remote history"
echo "Press Ctrl+C to cancel, or wait 3 seconds..."
sleep 3

git push -f origin main

echo ""
echo "✅ Done! Repository pushed with clean history (no secrets)."
echo "🔗 Repository: https://github.com/panchovial-max/PVB-NEW-WEB"


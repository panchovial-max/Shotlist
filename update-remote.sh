#!/bin/bash
# Script to update git remote after renaming repository on GitHub

echo "🔄 Updating git remote to PVB-NEW-WEB..."

# Update remote URL
git remote set-url origin https://github.com/panchovial-max/PVB-NEW-WEB.git

# Verify it worked
echo ""
echo "✅ Remote updated! Current remotes:"
git remote -v

echo ""
echo "✨ Done! Your repository is now connected to PVB-NEW-WEB"
echo ""
echo "Next steps:"
echo "1. Make sure you renamed the repository on GitHub first"
echo "2. Push your changes: git push origin main"


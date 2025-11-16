#!/bin/bash
# Fix npm permission issues by cleaning and reinstalling

echo "🔧 Fixing npm permissions and reinstalling dependencies..."

cd "$(dirname "$0")"

# Step 1: Remove corrupted node_modules
echo "📦 Removing node_modules..."
rm -rf node_modules

# Step 2: Remove package-lock.json (optional, but helps with fresh install)
echo "📦 Removing package-lock.json..."
rm -f package-lock.json

# Step 3: Clear npm cache
echo "🧹 Clearing npm cache..."
npm cache clean --force

# Step 4: Fix npm permissions (if needed)
echo "🔐 Checking npm permissions..."
npm config set prefix ~/.npm-global 2>/dev/null || true

# Step 5: Reinstall dependencies
echo "⬇️  Installing dependencies (this may take a few minutes)..."
npm install

echo ""
echo "✅ Done! Try running 'npm run dev' now."
echo ""


#!/bin/bash
# Quick script to rebuild virtual environment

echo "🔧 Rebuilding virtual environment..."

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Remove corrupted venv
if [ -d "$PROJECT_ROOT/.venv" ]; then
    echo "📦 Removing old .venv..."
    rm -rf "$PROJECT_ROOT/.venv"
fi

# Create fresh venv
echo "🆕 Creating new virtual environment..."
python3 -m venv "$PROJECT_ROOT/.venv"

# Activate it
echo "✅ Activating virtual environment..."
source "$PROJECT_ROOT/.venv/bin/activate"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install backend dependencies
echo "📚 Installing dependencies..."
cd "$PROJECT_ROOT/backend"
pip install -r requirements.txt

echo ""
echo "✅ Virtual environment rebuilt successfully!"
echo ""
echo "To use it:"
echo "  source .venv/bin/activate"
echo "  cd backend"
echo "  ./start.sh"


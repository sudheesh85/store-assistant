#!/bin/bash
# Helper script to start backend - automatically kills any existing process on port 8000

# Get the backend directory (where this script is located)
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the project root directory (parent of backend/)
PROJECT_ROOT="$(cd "$BACKEND_DIR/.." && pwd)"

echo "🔍 Checking port 8000..."
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000 in use. Killing existing process..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 1
    echo "✅ Port cleared"
fi

echo "🚀 Starting backend (without reload to avoid multiprocessing errors)..."
# Change to backend directory and run uvicorn
cd "$BACKEND_DIR"
"$PROJECT_ROOT/.venv/bin/python" -m uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info


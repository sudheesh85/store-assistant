#!/bin/bash
# Helper script to stop backend

echo "🛑 Stopping backend..."
if lsof -ti:8000 > /dev/null 2>&1; then
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    echo "✅ Backend stopped (port 8000 freed)"
else
    echo "ℹ️  No backend process found on port 8000"
fi


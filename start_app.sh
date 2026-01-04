#!/bin/bash

# Expense Tracker - Quick Start Script
# Usage: ./start_app.sh

cd "$(dirname "$0")"

# Kill any existing Flask processes
pkill -f "python3 app.py" 2>/dev/null || true
sleep 1

# Set environment variables
export OPENAI_API_KEY=${OPENAI_API_KEY:-'sk-test-demo'}
export FLASK_ENV=${FLASK_ENV:-'development'}
export SECRET_KEY=${SECRET_KEY:-'test-secret'}
export PORT=${PORT:-8888}

echo "🚀 Starting Expense Tracker..."
echo "   FLASK_ENV: $FLASK_ENV"
echo "   PORT: $PORT"
echo ""
echo "📍 Open your browser: http://127.0.0.1:$PORT"
echo ""
echo "To stop: Press Ctrl+C"
echo ""

python3 app.py

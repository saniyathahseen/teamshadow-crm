#!/bin/bash
echo "========================================="
echo "Team Shadow Weddings - CRM System"
echo "========================================="
echo ""

# Check if backend is already running
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Backend server is already running on port 8000"
else
    echo "🚀 Starting backend server..."
    cd "$(dirname "$0")/backend"
    source venv/bin/activate
    python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    echo "✅ Backend started (PID: $BACKEND_PID)"
    sleep 2
fi

echo ""
echo "📋 API running at: http://localhost:8000"
echo "📋 API Docs at:    http://localhost:8000/docs"
echo ""
echo "🌐 Frontend: Open 'frontend/index.html' in your browser"
echo ""
echo "🔐 Environment configuration required before first login."
echo "Set TEAMSHADOW_ADMIN_USERNAME, TEAMSHADOW_ADMIN_PASSWORD, and TEAMSHADOW_STAFF_PASSWORD in your shell or .env file."
echo ""
echo "========================================="
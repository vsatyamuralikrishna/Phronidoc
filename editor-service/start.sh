#!/bin/bash

# Phronidoc Documentation Editor Service Startup Script

echo "🚀 Starting Phronidoc Documentation Editor Service..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Start backend server
echo "🌐 Starting backend server on http://localhost:8001..."
uvicorn main:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Navigate to frontend directory
cd ../frontend

# Start frontend server
echo "🎨 Starting frontend server on http://localhost:8080..."
python3 -m http.server 8080 &
FRONTEND_PID=$!

echo ""
echo "✅ Services started!"
echo ""
echo "📝 Editor: http://localhost:8080"
echo "🔌 API: http://localhost:8001"
echo "📚 API Docs: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait

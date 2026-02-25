#!/bin/bash

echo "🛡️  Starting Threat Intelligence Toolkit..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Start backend
echo "🚀 Starting backend server..."
cd backend
python app.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend (simple HTTP server)
echo "🌐 Starting frontend server..."
cd ../frontend
python -m http.server 8000 &
FRONTEND_PID=$!

echo ""
echo "✅ TIT is running!"
echo "📱 Frontend: http://localhost:8000"
echo "🔌 Backend: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait

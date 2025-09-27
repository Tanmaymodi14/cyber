#!/bin/bash

# Check if Python virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    if [ -f ".env" ]; then
        echo "Loading environment variables from .env file..."
        export $(grep -v '^#' .env | xargs)
    else
        echo "Warning: OPENAI_API_KEY is not set. AI analysis features will not work."
    fi
fi

# Start backend in background
echo "Starting backend server..."
python src/api_server.py &
BACKEND_PID=$!

# Navigate to frontend directory
cd Frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start frontend
echo "Starting frontend server..."
npm run dev

# Cleanup when frontend exits
echo "Shutting down backend server..."
kill $BACKEND_PID

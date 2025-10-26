#!/bin/bash

# Quick start script for Truck Monitoring System

echo "🚀 Starting Truck Monitoring System..."

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source backend/venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -q -r backend/requirements.txt

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  No .env file found, copying from env.example..."
    cp backend/env.example backend/.env
    echo "⚠️  Please edit backend/.env with your MySQL credentials!"
fi

# Start the server
echo "🚀 Starting server on port 8095..."
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8095 --reload


#!/bin/bash

# Exercise 11 Frontend Startup Script
# This script ensures a clean Next.js startup

echo "🧹 Cleaning up old processes..."
killall -9 node 2>/dev/null || true
sleep 2

echo "📁 Navigating to frontend directory..."
cd "$(dirname "$0")"

echo "🗑️  Removing build cache..."
rm -rf .next

echo "📦 Installing dependencies..."
npm install

echo "🚀 Starting Next.js dev server on port 3082..."
npm run dev


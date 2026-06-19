#!/bin/bash
# Amazon Listing Analyzer - Frontend
cd "$(dirname "$0")/frontend"
npm install --silent 2>/dev/null
echo "Starting frontend on http://localhost:5173"
npx vite --host 0.0.0.0

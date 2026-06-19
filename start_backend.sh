#!/bin/bash
# Amazon Listing Analyzer - Backend
cd "$(dirname "$0")/backend"
pip install -r requirements.txt -q 2>/dev/null
echo "Starting backend on http://localhost:8000"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

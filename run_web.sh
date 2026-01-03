#!/bin/bash

# Quick startup script for the web interface

echo "Starting TradingView Backtest Web Interface..."
echo "=============================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup..."
    ./setup.sh
fi

# Activate venv and run app
source venv/bin/activate
streamlit run app.py

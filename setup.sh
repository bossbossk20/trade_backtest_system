#!/bin/bash

# Setup script for TradingView Backtest System

echo "Setting up TradingView Backtest System..."
echo "=========================================="

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the backtest:"
echo "  python main.py"
echo ""
echo "To deactivate when done:"
echo "  deactivate"
echo "=========================================="

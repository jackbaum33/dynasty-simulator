#!/bin/bash

# Fantasy Football Simulator - Quick Start Script

echo "🏈 Fantasy Football Schedule Simulator"
echo "======================================"
echo ""

# Check if Flask is installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Installing Flask..."
    pip install flask
    echo ""
fi

echo "🚀 Starting web server..."
echo ""
echo "Once started, open your browser to:"
echo "   http://localhost:5000"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

python app.py
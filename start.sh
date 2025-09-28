#!/bin/bash

# Noah's AI Assistant Startup Script

echo "🤖 Starting Noah's AI Assistant..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your OpenAI API key"
    echo ""
fi

# Install requirements if needed
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "🚀 Starting application..."
echo ""
echo "Choose your mode:"
echo "  1) Full version (requires OpenAI API key)"
echo "  2) Demo version (works without API key)"
echo ""

read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo "🔑 Starting full version with OpenAI integration..."
        streamlit run app.py
        ;;
    2)
        echo "🎯 Starting demo version..."
        streamlit run demo.py
        ;;
    *)
        echo "❌ Invalid choice. Starting demo version by default..."
        streamlit run demo.py
        ;;
esac
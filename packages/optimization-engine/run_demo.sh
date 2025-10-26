#!/bin/bash

# Load Groq API key from web .env file
if [ -f "../../apps/web/.env" ]; then
    export GROQ_API_KEY=$(grep GROQ_KEY ../../apps/web/.env | cut -d '=' -f2)
    echo "✓ Loaded Groq API key from apps/web/.env"
else
    echo "❌ Error: apps/web/.env not found"
    exit 1
fi

echo ""
echo "🚀 Starting AI-Powered Operational Recommendation Demo"
echo ""

# Run the demo
python demo_ai_recommendations.py

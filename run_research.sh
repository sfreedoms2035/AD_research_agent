#!/bin/bash

# Automated Driving Research Agent Runner
# ======================================

echo "Automated Driving Research Agent"
echo "================================="
echo

# Check if API key is provided as argument
if [ -z "$1" ]; then
    echo "ERROR: Please provide your API key as an argument"
    echo
    echo "Usage: ./run_research.sh YOUR_API_KEY"
    echo
    echo "Get your API key from:"
    echo " - Google AI Studio: https://aistudio.google.com/"
    echo " - Kimi AI: https://platform.moonshot.cn/"
    echo
    exit 1
fi

# Run the research agent
echo "Starting research with Gemini Pro..."
echo
python3 enhanced_ad_research_agent.py --api-key "$1" --model gemini

if [ $? -eq 0 ]; then
    echo
    echo "Research completed successfully!"
else
    echo
    echo "Research failed with error code $?"
fi

echo
read -p "Press Enter to continue..."

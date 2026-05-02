#!/bin/bash

echo ""
echo "TasksStatusBot Environment Setup"
echo "============================"
echo ""

read -p "Enter your Groq API key: " GROQ_KEY

echo "GROQ_API_KEY=$GROQ_KEY" > .env

echo ""
echo "✓ .env file created!"
echo ""
echo "Now activate venv and run:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
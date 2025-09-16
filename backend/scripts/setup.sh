#!/bin/bash

# Scientific Text Annotator - Backend Setup Script

echo "🚀 Setting up Scientific Text Annotator Backend..."

# Check if Python 3.11+ is installed
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')
if [ -z "$python_version" ] || [ $(echo "$python_version < 3.11" | bc) -eq 1 ]; then
    echo "❌ Python 3.11+ is required. Please install Python 3.11 or higher."
    exit 1
fi
echo "✅ Python $python_version detected"

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file..."
    cp .env.example .env
    echo "⚠️ Please update the .env file with your actual configuration values"
fi

# Create uploads directory
mkdir -p uploads

echo "✅ Backend setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your database and API keys"
echo "2. Set up PostgreSQL database"
echo "3. Run migrations: alembic upgrade head"
echo "4. Start the server: uvicorn main:app --reload"
echo ""
echo "Or use Docker Compose:"
echo "1. Update .env file"
echo "2. Run: docker-compose up -d"

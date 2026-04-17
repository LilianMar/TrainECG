#!/bin/bash
# setup.sh - Script de setup automático para ECG Backend

set -e  # Exit on error

echo "=========================================="
echo "ECG Insight Mentor - Backend Setup"
echo "=========================================="
echo ""

# Check Python version
echo "✓ Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Python $python_version detected"

# Create virtual environment
echo ""
echo "✓ Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo ""
echo "✓ Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install requirements
echo ""
echo "✓ Installing dependencies..."
pip install -r requirements.txt

# Create .env file
echo ""
echo "✓ Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  .env file created (edit with your values)"
else
    echo "  .env file already exists"
fi

# Create necessary directories
echo ""
echo "✓ Creating directories..."
mkdir -p logs
mkdir -p uploads
mkdir -p models
echo "  logs/, uploads/, models/ directories created"

# Display next steps
echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration:"
echo "   - DATABASE_URL (default: SQLite)"
echo "   - SECRET_KEY (change to random string)"
echo "   - OPENAI_API_KEY (OpenAI API key)"
echo "   - MODEL_PATH (path to .h5 model file)"
echo ""
echo "2. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run the development server:"
echo "   python run.py"
echo ""
echo "4. Visit API docs:"
echo "   http://localhost:8000/docs"
echo ""
echo "=========================================="

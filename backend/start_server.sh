# Quick Start Script for Unix/Linux/Mac

echo "========================================"
echo "Med-Chatbot Backend Quick Start"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Install dependencies
echo "Installing/Updating dependencies..."
pip install -r requirements.txt
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    echo ""
    exit 1
fi
echo ""

echo "========================================"
echo "Starting FastAPI server..."
echo "========================================"
echo "API Documentation: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"
echo "========================================"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

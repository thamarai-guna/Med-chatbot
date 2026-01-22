@echo off
echo ========================================
echo Med-Chatbot Backend Quick Start
echo ========================================
echo.

echo Checking if virtual environment exists...
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo Installing/Updating dependencies...
pip install -r requirements.txt
echo.

echo Checking .env file...
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and configure it.
    echo.
    pause
    exit /b 1
)
echo.

echo ========================================
echo Starting FastAPI server...
echo ========================================
echo API Documentation: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo ========================================
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

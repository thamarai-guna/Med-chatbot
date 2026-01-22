@echo off
REM Med-Chatbot Startup Script (Windows)
REM This script starts the backend and frontend servers

echo ============================================
echo    Med-Chatbot - Healthcare Platform
echo    Starting all services...
echo ============================================
echo.

REM Check if backend virtual environment exists
if not exist "backend\venv" (
    echo [ERROR] Backend virtual environment not found!
    echo Please run setup first:
    echo   cd backend
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check if frontend node_modules exists
if not exist "frontend\node_modules" (
    echo [ERROR] Frontend dependencies not installed!
    echo Please run setup first:
    echo   cd frontend
    echo   npm install
    pause
    exit /b 1
)

echo [1/2] Starting Backend Server...
start cmd /k "cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul

echo [2/2] Starting Frontend Server...
start cmd /k "cd frontend && npm start"
timeout /t 3 /nobreak >nul

echo.
echo ============================================
echo    All services started!
echo ============================================
echo.
echo Backend API: http://localhost:8000
echo Frontend App: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo To stop services, close the terminal windows.
echo.
pause

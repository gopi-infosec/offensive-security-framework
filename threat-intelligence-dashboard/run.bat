@echo off
title Threat Intelligence Toolkit

echo.
echo ========================================
echo  🛡️  Threat Intelligence Toolkit
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "backend\venv" (
    echo ❌ Virtual environment not found!
    echo ⚠️  Please run install.bat first
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist "backend\.env" (
    echo ❌ .env file not found!
    echo ⚠️  Please copy backend\.env.example to backend\.env and add your API keys
    pause
    exit /b 1
)

echo ✅ Starting Threat Intelligence Toolkit...
echo.

REM Start backend server in new window
echo 🚀 Starting backend server on http://localhost:5000
start "TIT Backend" cmd /k "cd backend && venv\Scripts\activate && python app.py"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend server in new window
echo 🚀 Starting frontend server on http://localhost:8000
start "TIT Frontend" cmd /k "cd frontend && python -m http.server 8000"

REM Wait for frontend to start
timeout /t 2 /nobreak >nul

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ✅ Application is running!
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 🌐 Open your browser and navigate to:
echo    http://localhost:8000
echo.
echo 📊 Backend API available at:
echo    http://localhost:5000/api
echo.
echo 💡 Close the backend and frontend windows to stop the servers
echo.
pause

@echo off
echo 🛑 Stopping Threat Intelligence Toolkit servers...
echo.

REM Kill Python processes on port 5000 (backend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
    if not errorlevel 1 (
        echo ✅ Backend server stopped (Port 5000)
    )
)

REM Kill Python processes on port 8000 (frontend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
    if not errorlevel 1 (
        echo ✅ Frontend server stopped (Port 8000)
    )
)

echo.
echo ✅ All servers stopped
pause

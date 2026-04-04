@echo off
REM Start ChemRAG Backend and Frontend servers in separate windows
REM This script launches both servers for development

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo.
echo ========================================
echo  ChemRAG - Start All Services
echo ========================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo [!] .env file not found
    echo Please copy .env.example to .env:
    echo   copy .env.example .env
    pause
    exit /b 1
)
echo [✓] Configuration file (.env) found

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo [!] Virtual environment not found
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)
echo [✓] Virtual environment found

REM Check if Node.js is installed
where node >nul 2>nul
if errorlevel 1 (
    echo [!] Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)
echo [✓] Node.js found

echo.
echo Launching backend and frontend servers...
echo.
echo Backend will start at: http://localhost:8000
echo Frontend will start at: http://localhost:5173
echo.
echo Two new windows will open for each service.
echo Press Ctrl+C in each window to stop the service.
echo.

REM Start backend in new window
echo Starting backend...
start "ChemRAG Backend" cmd /k call start_backend.bat

REM Wait a moment for backend to start
timeout /t 3 /nobreak

REM Start frontend in new window
echo Starting frontend...
start "ChemRAG Frontend" cmd /k call start_frontend.bat

echo.
echo All services started!
echo.
pause

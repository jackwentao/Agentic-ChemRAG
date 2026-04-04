@echo off
REM Start ChemRAG Backend Server
REM This script activates the virtual environment and starts the FastAPI backend

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo.
echo ========================================
echo  ChemRAG Backend Server
echo ========================================
echo.

REM Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo [✓] Virtual environment activated
) else (
    echo [!] Virtual environment not found at .venv
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo [!] .env file not found
    echo Please copy .env.example to .env and configure:
    echo   copy .env.example .env
    pause
    exit /b 1
)
echo [✓] Configuration file (.env) found

REM Check if requirements are installed
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo [!] Dependencies not installed
    echo Installing requirements...
    pip install -r backend\requirements.txt
    echo [✓] Dependencies installed
)

REM Display info
echo [✓] All checks passed
echo.
echo Launching backend server...
echo   Backend URL: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.

REM Start backend
cd /d "%SCRIPT_DIR%\backend"
python main.py

pause

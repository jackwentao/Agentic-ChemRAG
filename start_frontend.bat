@echo off
REM Start ChemRAG Frontend Development Server
REM This script installs dependencies and starts the Vite dev server

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%\frontend"

echo.
echo ========================================
echo  ChemRAG Frontend Dev Server
echo ========================================
echo.

REM Check if Node modules are installed
if not exist "node_modules" (
    echo [!] Dependencies not installed
    echo Installing npm packages...
    call npm install
    echo [✓] Dependencies installed
) else (
    echo [✓] Node modules found
)

REM Check if .env exists in parent directory
if not exist ".\..\.env" (
    echo [!] .env file not found in project root
    echo Please run from the root directory and ensure .env exists
    pause
    exit /b 1
)
echo [✓] Configuration file (.env) found

REM Display info
echo [✓] All checks passed
echo.
echo Launching frontend dev server...
echo   Frontend URL: http://localhost:5173
echo.

REM Start dev server
call npm run dev

pause

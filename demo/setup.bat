@echo off
echo ========================================
echo AI Ticket Classifier - Quick Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo [1/4] Installing dependencies...
pip install -r requirements.txt

echo.
echo [2/4] Checking for .env file...
if not exist .env (
    echo Creating .env from template...
    copy .env.example .env
    echo.
    echo ========================================
    echo IMPORTANT: Edit .env and add your OpenAI API key!
    echo ========================================
    echo.
    pause
)

echo.
echo [3/4] Setup complete!
echo.
echo [4/4] Starting demo...
echo.

streamlit run demo_app.py

pause

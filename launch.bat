@echo off
REM Universal Music Track Downloader - Windows Launcher
REM This script launches the GUI application

title Universal Music Track Downloader

echo ========================================
echo   Universal Music Track Downloader
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Check if required packages are installed
echo Checking dependencies...
python -c "import yt_dlp" >nul 2>&1
if errorlevel 1 (
    echo [!] Installing missing dependencies...
    pip install -r requirements.txt
)

echo [OK] Dependencies ready
echo.

REM Launch the GUI
echo Launching application...
echo.
python downloader_gui.py

if errorlevel 1 (
    echo.
    echo [ERROR] Application closed with errors
    pause
)

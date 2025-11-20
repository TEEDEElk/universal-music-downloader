@echo off
REM Automated FFmpeg Installer for Windows
REM This script checks for and installs FFmpeg using Chocolatey

title FFmpeg Installer for Music Downloader

echo ================================================
echo   FFmpeg Installation Helper
echo ================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] This script requires Administrator privileges
    echo.
    echo Please right-click this file and select "Run as Administrator"
    echo.
    pause
    exit /b 1
)

echo [OK] Running with Administrator privileges
echo.

REM Check if FFmpeg is already installed
where ffmpeg >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] FFmpeg is already installed!
    ffmpeg -version | findstr "version"
    echo.
    goto :check_python_tools
)

echo [!] FFmpeg not found. Installing...
echo.

REM Check if Chocolatey is installed
where choco >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] Chocolatey not found. Installing Chocolatey...
    echo.
    
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    
    if %errorLevel% neq 0 (
        echo [ERROR] Failed to install Chocolatey
        echo.
        echo Please install FFmpeg manually:
        echo 1. Download from: https://www.gyan.dev/ffmpeg/builds/
        echo 2. Extract to C:\ffmpeg
        echo 3. Add C:\ffmpeg\bin to PATH
        echo.
        pause
        exit /b 1
    )
    
    REM Refresh environment
    call refreshenv
    echo [OK] Chocolatey installed successfully
    echo.
)

echo [!] Installing FFmpeg via Chocolatey...
echo.
choco install ffmpeg -y

if %errorLevel% neq 0 (
    echo [ERROR] Failed to install FFmpeg
    pause
    exit /b 1
)

echo.
echo [OK] FFmpeg installed successfully!
echo.

:check_python_tools

echo Checking Python tools...
echo.

REM Check yt-dlp
where yt-dlp >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] yt-dlp not in PATH
    echo [!] Trying to add Python Scripts to PATH...
    
    for /f "delims=" %%i in ('python -c "import sys; print(sys.executable.replace('python.exe', 'Scripts'))"') do set PYTHON_SCRIPTS=%%i
    echo Found Python Scripts: %PYTHON_SCRIPTS%
    
    REM Add to PATH temporarily
    set PATH=%PATH%;%PYTHON_SCRIPTS%
    
    echo [!] Testing yt-dlp again...
    where yt-dlp >nul 2>&1
    if %errorLevel% equ 0 (
        echo [OK] yt-dlp is now accessible
    ) else (
        echo [WARNING] yt-dlp still not found
        echo You may need to add this to PATH manually: %PYTHON_SCRIPTS%
    )
) else (
    echo [OK] yt-dlp found
)

echo.
echo ================================================
echo   Installation Complete!
echo ================================================
echo.
echo Next steps:
echo 1. Close and reopen PowerShell/Command Prompt
echo 2. Run: python downloader_gui.py
echo.
echo If tools are still not found, add to PATH:
for /f "delims=" %%i in ('python -c "import sys; print(sys.executable.replace('python.exe', 'Scripts'))"') do echo %%i
echo.
pause

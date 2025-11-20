#!/bin/bash
# Universal Music Track Downloader - Unix/macOS Launcher
# This script launches the GUI application

clear
echo "========================================"
echo "  Universal Music Track Downloader"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.7+ from https://www.python.org/"
    exit 1
fi

echo "[OK] Python found: $(python3 --version)"
echo ""

# Check if required packages are installed
echo "Checking dependencies..."
if ! python3 -c "import yt_dlp" &> /dev/null; then
    echo "[!] Installing missing dependencies..."
    pip3 install -r requirements.txt
fi

echo "[OK] Dependencies ready"
echo ""

# Check for ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "[WARNING] ffmpeg not found in PATH"
    echo "Please install ffmpeg:"
    echo "  macOS: brew install ffmpeg"
    echo "  Linux: sudo apt install ffmpeg"
    echo ""
fi

# Launch the GUI
echo "Launching application..."
echo ""
python3 downloader_gui.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Application closed with errors"
    read -p "Press Enter to exit..."
fi

# 🔧 Windows Installation Guide

## ❌ Problem: "The system cannot find the file specified"

This error means **FFmpeg** and the Python scripts (yt-dlp, spotdl) are not in your Windows PATH.

---

## ✅ Solution: Install FFmpeg

### Option 1: Using Chocolatey (Easiest)

1. **Install Chocolatey** (if not installed):
   - Open PowerShell as Administrator
   - Run:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```

2. **Install FFmpeg**:
   ```powershell
   choco install ffmpeg
   ```

3. **Restart your terminal** and verify:
   ```powershell
   ffmpeg -version
   ```

### Option 2: Manual Installation

1. **Download FFmpeg**:
   - Go to: https://www.gyan.dev/ffmpeg/builds/
   - Download: **ffmpeg-release-essentials.zip**

2. **Extract**:
   - Extract to: `C:\ffmpeg`
   - You should have: `C:\ffmpeg\bin\ffmpeg.exe`

3. **Add to PATH**:
   - Press `Win + X` → System
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", find "Path"
   - Click "Edit" → "New"
   - Add: `C:\ffmpeg\bin`
   - Click OK on all dialogs

4. **Restart PowerShell** and verify:
   ```powershell
   ffmpeg -version
   ```

---

## ✅ Fix Python Scripts PATH

The Python packages are installed but not in PATH. Add this directory:

1. **Find your Python Scripts directory**:
   ```powershell
   python -c "import sys; print(sys.executable.replace('python.exe', 'Scripts'))"
   ```

2. **Add to PATH** (same steps as FFmpeg):
   - The path will be something like:
   ```
   C:\Users\YourName\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts
   ```

3. **Verify**:
   ```powershell
   yt-dlp --version
   spotdl --version
   ```

---

## 🚀 Quick Test After Installation

1. **Restart PowerShell** (important!)
2. **Verify all tools**:
   ```powershell
   ffmpeg -version
   yt-dlp --version
   spotdl --version
   ```

3. **Run the app**:
   ```powershell
   python downloader_gui.py
   ```

---

## 🆘 Still Having Issues?

### Alternative: Use Python Module Calls

Instead of relying on PATH, you can run commands directly:

```powershell
# Instead of: yt-dlp
python -m yt_dlp

# Instead of: spotdl
python -m spotdl
```

Let me know if you need a modified version that doesn't require PATH setup!

---

## 📝 Summary

**What you need:**
1. ✅ Python packages (already installed via pip)
2. ❌ FFmpeg executable → Install from link above
3. ❌ Python Scripts in PATH → Add Scripts folder to PATH

**Once done, the app will work perfectly!** 🎵

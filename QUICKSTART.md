# 🚀 Quick Start Guide

## First Time Setup (5 minutes)

### 1. Install Dependencies

**Windows:**
```powershell
# Install Python packages
pip install -r requirements.txt

# Download FFmpeg from https://ffmpeg.org/
# Add ffmpeg.exe to your PATH
```

**macOS:**
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install ffmpeg
pip3 install -r requirements.txt
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg python3-pip
pip3 install -r requirements.txt
```

### 2. Launch the Application

**Windows:**
- Double-click `launch.bat`, or
- Run: `python downloader_gui.py`

**macOS/Linux:**
```bash
chmod +x launch.sh
./launch.sh
```

---

## 📝 Using the Application

### Download a Single Track

1. **Select Platform**: Choose SoundCloud or Spotify
2. **Choose Format**: MP3 (320kbps) or WAV
3. **Paste URL**: Copy and paste track URL
4. **Click "Add to Queue"**
5. **Click "Start Download"**

### Batch Download Multiple Tracks

1. Paste first URL → Click "Add to Queue"
2. Paste second URL → Click "Add to Queue"
3. Repeat for all tracks
4. Click "Start Download" (processes all at once)

### Download Entire Playlist/Album

1. Copy the playlist or album URL
2. Paste into URL field
3. Click "Add to Queue"
4. Click "Start Download"
5. All tracks will be downloaded sequentially

---

## 🎯 Example URLs

### SoundCloud
```
https://soundcloud.com/artist/track-name
https://soundcloud.com/artist/sets/playlist-name
```

### Spotify
```
https://open.spotify.com/track/7qiZfU4dY1lWllzX7mPBB0
https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy
https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
```

---

## ⚙️ Settings

### Change Output Directory
1. Click "Browse" next to Output Directory
2. Select folder where you want files saved
3. Default: `~/Downloads/Music`

### Audio Quality
- **MP3**: 320kbps (8-10 MB per song)
- **WAV**: Lossless (40-50 MB per song)

---

## 🐛 Troubleshooting

### "Missing dependencies" error
```bash
pip install --upgrade yt-dlp spotdl mutagen requests
```

### "ffmpeg not found"
- Windows: Add ffmpeg.exe to PATH
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

### Download fails
- Check URL is valid
- Ensure internet connection
- Some content may be region-locked

### GUI doesn't open
```bash
python downloader_gui.py
# Check terminal for error messages
```

---

## 💡 Tips & Tricks

1. **Queue Multiple Downloads**: Add all tracks first, then start downloading
2. **Monitor Log**: Activity log shows detailed progress
3. **Check Output Folder**: Files appear in real-time as they download
4. **Use Playlists**: Download entire collections at once
5. **Metadata Included**: All files have proper tags and artwork

---

## 📊 What Gets Downloaded

Each track includes:
- ✅ Audio file (MP3/WAV)
- ✅ Track title
- ✅ Artist name
- ✅ Album name
- ✅ Release year
- ✅ Album artwork (embedded)

---

## ⚠️ Legal Notice

**For Educational Purposes Only**

- Only download content you have rights to
- Respect copyright laws
- Support artists by purchasing music
- Don't redistribute downloaded content

---

## 🆘 Need Help?

1. Check the full [README.md](README.md)
2. Review error messages in Activity Log
3. Verify all dependencies are installed
4. Test with a single track first

---

**Enjoy your music! 🎵**

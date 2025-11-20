# 🎵 Universal Music Track Downloader

A powerful desktop application for downloading music from **SoundCloud**, **Spotify**, and **Apple Music** with support for high-quality 320kbps MP3 and lossless WAV formats. Features include metadata preservation, album art embedding, batch downloads, and a modern GUI with download queue management.

---

## ✨ Features

### 🎯 Core Capabilities
- **Multi-Platform Support**: Download from SoundCloud, Spotify, and Apple Music
- **High-Quality Audio**: 
  - 320kbps MP3 (near-lossless quality)
  - WAV format (CD-quality lossless audio)
- **Metadata Preservation**: Automatic tagging with title, artist, album, and release year
- **Album Art Embedding**: Downloads and embeds cover artwork into files
- **Batch Downloads**: Queue multiple tracks, playlists, or albums
- **Playlist/Album Support**: Download entire collections in one go

### 🖥️ User Interface
- Modern Tkinter-based GUI
- Real-time download progress tracking
- Download queue management
- Activity log with timestamps
- Configurable output directory
- Error handling with detailed feedback

### 🛠️ Technical Features
- Cross-platform (Windows, macOS, Linux)
- Command-line interface available
- Parallel metadata processing
- Robust error handling and logging
- Memory-efficient streaming downloads

---

## 📋 Requirements

### System Requirements
- **Python 3.7 or higher**
- **FFmpeg** - Audio processing engine ([Download](https://ffmpeg.org/))
- Stable internet connection

### Python Dependencies
All Python packages are listed in `requirements.txt`:
- `yt-dlp` - YouTube/SoundCloud downloader
- `spotdl` - Spotify track downloader
- `mutagen` - Audio metadata library
- `requests` - HTTP library for downloading artwork

---

## 🚀 Installation

### Step 1: Clone or Download
```bash
git clone https://github.com/yourusername/music-downloader.git
cd music-downloader
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Install FFmpeg
**Windows:**
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract and add to PATH environment variable

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

### Step 4: Verify Installation
```bash
ffmpeg -version
yt-dlp --version
spotdl --version
```

---

## 📖 Usage

### GUI Application (Recommended)

```bash
python downloader_gui.py
```

**Steps:**
1. Select platform (🎧 SoundCloud, 🎵 Spotify, or 🍎 Apple Music)
2. Choose output format (MP3 320kbps or WAV)
3. Paste track/playlist/album URL
4. Click "➕ Add to Queue" (repeat for batch downloads)
5. Click "⬇️ Start Download"
6. Monitor progress in the activity log

**Features:**
- Queue multiple downloads before starting
- Browse and select custom output directory
- Real-time status updates and logging
- Clear queue or remove individual items

### Command-Line Interface

```bash
# Download from SoundCloud as MP3
python downloader.py --soundcloud "https://soundcloud.com/artist/track" --format mp3

# Download from Spotify as WAV
python downloader.py --spotify "https://open.spotify.com/track/..." --format wav --output ./downloads

# Download from Apple Music as MP3
python downloader.py --applemusic "https://music.apple.com/us/album/..." --format mp3

# Download entire playlist
python downloader.py --spotify "https://open.spotify.com/playlist/..." --format mp3
```

**Command-Line Options:**
- `--soundcloud URL` - SoundCloud track/playlist URL
- `--spotify URL` - Spotify track/album/playlist URL
- `--applemusic URL` - Apple Music track/album/playlist URL
- `--format {mp3|wav}` - Output audio format
- `--output DIR` - Output directory (default: current directory)

---

## 🎯 Supported URLs

### SoundCloud
- Individual tracks: `https://soundcloud.com/artist/track-name`
- Playlists: `https://soundcloud.com/artist/sets/playlist-name`
- User's tracks: `https://soundcloud.com/artist/tracks`

### Spotify
- Tracks: `https://open.spotify.com/track/...`
- Albums: `https://open.spotify.com/album/...`
- Playlists: `https://open.spotify.com/playlist/...`

### Apple Music
- Tracks: `https://music.apple.com/us/album/track-name/...`
- Albums: `https://music.apple.com/us/album/...`
- Playlists: `https://music.apple.com/us/playlist/...`

---

## 📁 Output Structure

Downloaded files are organized as follows:

```
Output Directory/
├── Artist Name - Track Title.mp3
├── Artist Name - Track Title.wav
└── [Additional tracks...]
```

**Metadata Embedded:**
- Title
- Artist
- Album
- Release Year
- Album Artwork (embedded in file)

---

## 🔧 Technical Details

### Audio Quality Specifications

**MP3 Format:**
- Bitrate: 320 kbps (CBR)
- Sample Rate: 44.1 kHz
- Channels: Stereo
- Codec: LAME MP3

**WAV Format:**
- Codec: PCM (Uncompressed)
- Bit Depth: 16-bit
- Sample Rate: 44.1 kHz
- Channels: Stereo

### How It Works

1. **URL Parsing**: Extracts platform and content type from URL
2. **Metadata Extraction**: Retrieves track information via platform APIs
3. **Audio Download**: 
   - SoundCloud: Direct stream capture via yt-dlp
   - Spotify: Matches and downloads from YouTube via spotDL
4. **Quality Conversion**: FFmpeg re-encodes to target format and bitrate
5. **Metadata Embedding**: Mutagen writes ID3 tags and artwork
6. **File Organization**: Saves to specified output directory

---

## 🐛 Troubleshooting

### Common Issues

**"Missing dependencies" error:**
```bash
pip install --upgrade yt-dlp spotdl mutagen requests
```

**FFmpeg not found:**
- Ensure FFmpeg is installed and added to system PATH
- Test with: `ffmpeg -version`

**Spotify downloads fail:**
- spotDL relies on YouTube matching - some tracks may be unavailable
- Try downloading directly from YouTube if possible

**Permission denied errors:**
- Check write permissions for output directory
- Run with appropriate privileges if needed

**No audio in downloaded files:**
- Verify FFmpeg installation
- Check internet connection stability
- Some platforms may have region restrictions

---

## ⚖️ Legal & Ethical Considerations

### ⚠️ IMPORTANT DISCLAIMER

**This tool is provided for EDUCATIONAL PURPOSES ONLY.**

- ❌ Do NOT use to violate copyright laws
- ❌ Do NOT use to circumvent platform Terms of Service
- ❌ Do NOT redistribute downloaded content
- ✅ Only download content you have rights to
- ✅ Support artists by purchasing music legally
- ✅ Use for personal archival of owned content only

**Spotify Terms of Service**: Explicitly prohibits downloading content for offline use outside their official app.

**SoundCloud Terms of Service**: Only allows downloading of tracks where the artist has enabled the download button.

**The developers are not responsible for misuse of this software.**

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Submit a pull request

---

## 📝 License

This project is for educational purposes. See individual dependencies for their licenses:
- yt-dlp: [Unlicense](https://github.com/yt-dlp/yt-dlp/blob/master/LICENSE)
- spotDL: [MIT License](https://github.com/spotDL/spotify-downloader/blob/master/LICENSE)
- mutagen: [GPL-2.0](https://github.com/quodlibet/mutagen/blob/master/COPYING)

---

## 🙏 Acknowledgments

- **yt-dlp** - Powerful media downloader
- **spotDL** - Spotify track matching and download
- **mutagen** - Audio metadata manipulation
- **FFmpeg** - Audio/video processing framework

---

## 📞 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check existing issues for solutions
- Read the documentation thoroughly

---

**Made with ❤️ for music enthusiasts**

_Remember: Support your favorite artists by purchasing their music legally!_
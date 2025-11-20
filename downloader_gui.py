import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import subprocess
import os
import shutil
import json
import queue
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC, TDRC
from mutagen.wave import WAVE
import requests

# Get local FFmpeg path
SCRIPT_DIR = Path(__file__).parent
FFMPEG_LOCAL = SCRIPT_DIR / "ffmpeg" / "ffmpeg-8.0-essentials_build" / "bin" / "ffmpeg.exe"

def get_ffmpeg_path():
    """Get FFmpeg executable path (local or system)."""
    if FFMPEG_LOCAL.exists():
        return str(FFMPEG_LOCAL)
    return shutil.which("ffmpeg") or "ffmpeg"

def get_python_executable():
    """Get Python executable path."""
    return sys.executable

def is_exe(name):
    """Check if an executable is available in PATH or as Python module."""
    # Check if it's in PATH
    if shutil.which(name) is not None:
        return True
    
    # For Python packages, check if module exists
    if name == "yt-dlp":
        try:
            import yt_dlp
            return True
        except ImportError:
            return False
    elif name == "spotdl":
        try:
            import spotdl
            return True
        except ImportError:
            return False
    elif name == "ffmpeg":
        # Check local ffmpeg
        return FFMPEG_LOCAL.exists() or shutil.which("ffmpeg") is not None
    
    return False

def download_image(url: str, output_path: str) -> bool:
    """Download album art from URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception:
        return False

def get_metadata_from_file(file: str, info_json: str = None) -> Dict:
    """Extract metadata from file or info JSON."""
    metadata = {
        "title": "",
        "artist": "Unknown Artist",
        "album": "Unknown Album",
        "year": "",
        "artwork_url": None
    }
    
    try:
        if info_json and os.path.exists(info_json):
            with open(info_json, 'r', encoding='utf-8') as f:
                info = json.load(f)
                metadata['title'] = info.get('title', os.path.basename(file))
                metadata['artist'] = info.get('artist') or info.get('uploader', 'Unknown Artist')
                metadata['album'] = info.get('album', 'Unknown Album')
                metadata['year'] = str(info.get('release_year', ''))
                metadata['artwork_url'] = info.get('thumbnail')
        else:
            metadata['title'] = os.path.splitext(os.path.basename(file))[0]
    except Exception:
        metadata['title'] = os.path.splitext(os.path.basename(file))[0]
    
    return metadata

def set_mp3_metadata(file: str, metadata: Dict, cover: str = None):
    """Embed metadata into MP3 file."""
    try:
        audio = MP3(file, ID3=ID3)
        try:
            audio.add_tags()
        except:
            pass
        
        audio.tags["TIT2"] = TIT2(encoding=3, text=metadata["title"])
        audio.tags["TPE1"] = TPE1(encoding=3, text=metadata["artist"])
        audio.tags["TALB"] = TALB(encoding=3, text=metadata["album"])
        
        if metadata.get("year"):
            audio.tags["TDRC"] = TDRC(encoding=3, text=metadata["year"])
        
        if cover and os.path.exists(cover):
            with open(cover, 'rb') as img:
                audio.tags.add(
                    APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3,
                        desc='Cover',
                        data=img.read()
                    )
                )
        audio.save()
    except Exception as e:
        raise Exception(f"Failed to embed MP3 metadata: {e}")

def set_wav_metadata(file: str, metadata: Dict):
    """Embed metadata into WAV file."""
    try:
        audio = WAVE(file)
        audio["INAM"] = metadata["title"]
        audio["IART"] = metadata["artist"]
        audio["IPRD"] = metadata["album"]
        if metadata.get("year"):
            audio["ICRD"] = metadata["year"]
        audio.save()
    except Exception as e:
        raise Exception(f"Failed to embed WAV metadata: {e}")

def run_cmd(cmd: List[str], error_callback=None, output_callback=None, use_python_module=False, module_name=None):
    """Run command and capture output."""
    try:
        # If using Python module, prepend python -m
        if use_python_module and module_name:
            python_exe = get_python_executable()
            cmd = [python_exe, "-m", module_name] + cmd[1:]
        
        # Replace ffmpeg with local path if needed
        if cmd[0] == "ffmpeg":
            cmd[0] = get_ffmpeg_path()
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        for line in process.stdout:
            if output_callback:
                output_callback(line.strip())
        
        process.wait()
        if process.returncode != 0:
            stderr = process.stderr.read()
            raise subprocess.CalledProcessError(process.returncode, cmd, stderr)
            
    except subprocess.CalledProcessError as e:
        if error_callback:
            error_callback(f"Command failed: {' '.join(cmd)}\n{e}")
        raise
    except Exception as e:
        if error_callback:
            error_callback(f"Error: {e}")
        raise

def download_soundcloud(url: str, fmt: str, output_dir: str, status_callback, error_callback, log_callback):
    """Download from SoundCloud with metadata and album art."""
    status_callback("Downloading from SoundCloud...")
    log_callback(f"URL: {url}")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    out_template = str(output_path / "%(title)s.%(ext)s")
    
    # Use python -m yt_dlp if yt-dlp not in PATH
    use_module = shutil.which("yt-dlp") is None
    
    cmd = [
        "yt-dlp" if not use_module else "yt_dlp",
        "--extract-audio",
        "--audio-format", fmt,
        "--audio-quality", "0",
        "--embed-thumbnail",
        "--write-info-json",
        "--add-metadata",
        "--no-playlist",
        "--ignore-errors",
        "--no-overwrites",
        "--continue",
        "--ffmpeg-location", get_ffmpeg_path(),
        "-o", out_template,
        url
    ]
    
    if fmt == "mp3":
        cmd.extend(["--postprocessor-args", "ffmpeg:-b:a 320k -ar 44100"])
    
    run_cmd(cmd, error_callback=error_callback, output_callback=log_callback, 
            use_python_module=use_module, module_name="yt_dlp")
    
    # Find and process downloaded files
    downloaded_files = []
    for file in output_path.glob(f"*.{fmt}"):
        downloaded_files.append(str(file))
        
        # Process metadata and artwork
        info_file = str(file).replace(f'.{fmt}', '.info.json')
        metadata = get_metadata_from_file(str(file), info_file)
        
        if metadata['artwork_url']:
            artwork_path = str(file).replace(f'.{fmt}', '.jpg')
            if download_image(metadata['artwork_url'], artwork_path):
                if fmt == "mp3":
                    try:
                        set_mp3_metadata(str(file), metadata, artwork_path)
                    except Exception as e:
                        log_callback(f"Warning: {e}")
                os.remove(artwork_path)
        
        if os.path.exists(info_file):
            os.remove(info_file)
    
    if downloaded_files:
        status_callback(f"✅ Downloaded {len(downloaded_files)} file(s)")
        for f in downloaded_files:
            log_callback(f"Saved: {os.path.basename(f)}")
    else:
        error_callback("No files were downloaded.")
    
    return downloaded_files

def download_spotify(url: str, fmt: str, output_dir: str, status_callback, error_callback, log_callback):
    """Download from Spotify with metadata and album art."""
    status_callback("Downloading from Spotify...")
    log_callback(f"URL: {url}")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    original_dir = os.getcwd()
    os.chdir(output_path)
    
    try:
        # Use python -m spotdl if spotdl not in PATH
        use_module = shutil.which("spotdl") is None
        
        cmd = ['spotdl' if not use_module else 'spotdl', 
               '--format', 'mp3', 
               '--bitrate', '320k',
               '--ffmpeg', get_ffmpeg_path(),
               url]
        run_cmd(cmd, error_callback=error_callback, output_callback=log_callback,
                use_python_module=use_module, module_name="spotdl")
        
        status_callback("Processing files...")
        
        # Find downloaded MP3 files
        downloaded_files = []
        mp3_files = [f for f in os.listdir('.') if f.endswith('.mp3')]
        
        for mp3_file in mp3_files:
            if fmt == "wav":
                wav_file = mp3_file.replace('.mp3', '.wav')
                log_callback(f"Converting to WAV: {mp3_file}")
                
                subprocess.run([
                    get_ffmpeg_path(), "-y", "-i", mp3_file,
                    "-acodec", "pcm_s16le",
                    "-ar", "44100",
                    wav_file
                ], check=True, capture_output=True)
                
                # Transfer metadata to WAV
                try:
                    mp3_audio = MP3(mp3_file)
                    metadata = {
                        "title": str(mp3_audio.get("TIT2", "")),
                        "artist": str(mp3_audio.get("TPE1", "")),
                        "album": str(mp3_audio.get("TALB", "")),
                        "year": str(mp3_audio.get("TDRC", ""))
                    }
                    set_wav_metadata(wav_file, metadata)
                except Exception as e:
                    log_callback(f"Warning: Could not transfer metadata: {e}")
                
                os.remove(mp3_file)
                downloaded_files.append(str(output_path / wav_file))
                log_callback(f"Saved: {wav_file}")
            else:
                downloaded_files.append(str(output_path / mp3_file))
                log_callback(f"Saved: {mp3_file}")
        
        if downloaded_files:
            status_callback(f"✅ Downloaded {len(downloaded_files)} file(s)")
        else:
            error_callback("No files found after download.")
        
        return downloaded_files
    finally:
        os.chdir(original_dir)

def download_applemusic(url: str, fmt: str, output_dir: str, status_callback, error_callback, log_callback):
    """Download from Apple Music with metadata and album art."""
    status_callback("Downloading from Apple Music...")
    log_callback(f"URL: {url}")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    original_dir = os.getcwd()
    os.chdir(output_path)
    
    try:
        # spotDL also supports Apple Music URLs
        use_module = shutil.which("spotdl") is None
        
        cmd = ['spotdl' if not use_module else 'spotdl', 
               '--format', 'mp3', 
               '--bitrate', '320k',
               '--ffmpeg', get_ffmpeg_path(),
               url]
        run_cmd(cmd, error_callback=error_callback, output_callback=log_callback,
                use_python_module=use_module, module_name="spotdl")
        
        status_callback("Processing files...")
        
        # Find downloaded MP3 files
        downloaded_files = []
        mp3_files = [f for f in os.listdir('.') if f.endswith('.mp3')]
        
        for mp3_file in mp3_files:
            if fmt == "wav":
                wav_file = mp3_file.replace('.mp3', '.wav')
                log_callback(f"Converting to WAV: {mp3_file}")
                
                subprocess.run([
                    get_ffmpeg_path(), "-y", "-i", mp3_file,
                    "-acodec", "pcm_s16le",
                    "-ar", "44100",
                    wav_file
                ], check=True, capture_output=True)
                
                # Transfer metadata to WAV
                try:
                    mp3_audio = MP3(mp3_file)
                    metadata = {
                        "title": str(mp3_audio.get("TIT2", "")),
                        "artist": str(mp3_audio.get("TPE1", "")),
                        "album": str(mp3_audio.get("TALB", "")),
                        "year": str(mp3_audio.get("TDRC", ""))
                    }
                    set_wav_metadata(wav_file, metadata)
                except Exception as e:
                    log_callback(f"Warning: Could not transfer metadata: {e}")
                
                os.remove(mp3_file)
                downloaded_files.append(str(output_path / wav_file))
                log_callback(f"Saved: {wav_file}")
            else:
                downloaded_files.append(str(output_path / mp3_file))
                log_callback(f"Saved: {mp3_file}")
        
        if downloaded_files:
            status_callback(f"✅ Downloaded {len(downloaded_files)} file(s)")
        else:
            error_callback("No files found after download.")
        
        return downloaded_files
    finally:
        os.chdir(original_dir)

class DownloadQueue:
    """Manages download queue for batch processing."""
    def __init__(self):
        self.queue = queue.Queue()
        self.active = False
    
    def add(self, item: Dict):
        """Add download task to queue."""
        self.queue.put(item)
    
    def get(self):
        """Get next task from queue."""
        return self.queue.get()
    
    def is_empty(self):
        """Check if queue is empty."""
        return self.queue.empty()
    
    def size(self):
        """Get queue size."""
        return self.queue.qsize()


class App:
    def __init__(self, root):
        self.root = root
        root.title("Universal Music Track Downloader - SoundCloud & Spotify")
        root.geometry("800x700")
        
        # Variables
        self.platform = tk.StringVar(value="soundcloud")
        self.format = tk.StringVar(value="mp3")
        self.url = tk.StringVar()
        self.output_dir = tk.StringVar(value=str(Path.home() / "Downloads" / "Music"))
        self.status = tk.StringVar(value="Ready")
        
        # Download queue
        self.download_queue = DownloadQueue()
        self.is_downloading = False
        
        # UI Setup
        self.setup_ui()
        self.check_dependencies()
        
        # Create output directory
        Path(self.output_dir.get()).mkdir(parents=True, exist_ok=True)

    def setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Modern fonts
        self.title_font = ('Segoe UI', 16, 'bold')
        self.heading_font = ('Segoe UI', 10, 'bold')
        self.normal_font = ('Segoe UI', 9)
        self.button_font = ('Segoe UI', 9)
        self.log_font = ('Consolas', 9)
        self.status_font = ('Segoe UI', 9, 'bold')
        
        # Configure ttk style for modern look
        style = ttk.Style()
        style.configure('TLabelframe.Label', font=self.heading_font)
        style.configure('TButton', font=self.button_font)
        style.configure('TRadiobutton', font=self.normal_font)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="🎵 Universal Music Track Downloader",
            font=self.title_font
        )
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 15))
        
        # Platform selection
        platform_frame = ttk.LabelFrame(main_frame, text="Platform", padding="5")
        platform_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Radiobutton(
            platform_frame, 
            text='🎧 SoundCloud', 
            variable=self.platform, 
            value='soundcloud'
        ).grid(row=0, column=0, padx=10)
        
        ttk.Radiobutton(
            platform_frame, 
            text='🎵 Spotify', 
            variable=self.platform, 
            value='spotify'
        ).grid(row=0, column=1, padx=10)
        
        ttk.Radiobutton(
            platform_frame, 
            text='🍎 Apple Music', 
            variable=self.platform, 
            value='applemusic'
        ).grid(row=0, column=2, padx=10)
        
        # Format selection
        format_frame = ttk.LabelFrame(main_frame, text="Output Format", padding="5")
        format_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Radiobutton(
            format_frame, 
            text='MP3 (320kbps)', 
            variable=self.format, 
            value='mp3'
        ).grid(row=0, column=0, padx=10)
        
        ttk.Radiobutton(
            format_frame, 
            text='WAV (Lossless)', 
            variable=self.format, 
            value='wav'
        ).grid(row=0, column=1, padx=10)
        
        # URL input
        url_frame = ttk.LabelFrame(main_frame, text="Track/Playlist/Album URL", padding="5")
        url_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        url_frame.columnconfigure(0, weight=1)
        
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url, font=self.normal_font)
        self.url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
        self.url_entry.bind('<Return>', lambda e: self.add_to_queue())
        
        # Output directory
        output_frame = ttk.LabelFrame(main_frame, text="Output Directory", padding="5")
        output_frame.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(
            output_frame, 
            textvariable=self.output_dir, 
            font=self.normal_font
        ).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Button(
            output_frame, 
            text="Browse", 
            command=self.browse_output_dir
        ).grid(row=0, column=1, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=4, pady=10)
        
        self.add_button = ttk.Button(
            button_frame, 
            text="➕ Add to Queue", 
            command=self.add_to_queue,
            width=15
        )
        self.add_button.grid(row=0, column=0, padx=5)
        
        self.download_button = ttk.Button(
            button_frame, 
            text="⬇️ Start Download", 
            command=self.start_queue_processing,
            width=15
        )
        self.download_button.grid(row=0, column=1, padx=5)
        
        self.clear_button = ttk.Button(
            button_frame, 
            text="🗑️ Clear Queue", 
            command=self.clear_queue,
            width=15
        )
        self.clear_button.grid(row=0, column=2, padx=5)
        
        # Queue display
        queue_frame = ttk.LabelFrame(main_frame, text="Download Queue", padding="5")
        queue_frame.grid(row=6, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        queue_frame.columnconfigure(0, weight=1)
        queue_frame.rowconfigure(0, weight=1)
        
        self.queue_list = tk.Listbox(queue_frame, height=6, font=self.normal_font)
        self.queue_list.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        queue_scroll = ttk.Scrollbar(queue_frame, orient=tk.VERTICAL, command=self.queue_list.yview)
        queue_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.queue_list.config(yscrollcommand=queue_scroll.set)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=7, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        # Status
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=8, column=0, columnspan=4, sticky=(tk.W, tk.E))
        
        ttk.Label(
            status_frame, 
            textvariable=self.status, 
            font=self.status_font,
            foreground='#0066cc'
        ).grid(row=0, column=0, sticky=tk.W)
        
        # Log output
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="5")
        log_frame.grid(row=9, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=12, 
            font=self.log_font,
            wrap=tk.WORD
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        main_frame.rowconfigure(9, weight=2)
        
        # Disclaimer
        disclaimer = ttk.Label(
            main_frame,
            text="⚠️ For educational purposes only. Respect copyright and platform ToS.",
            font=('Segoe UI', 8),
            foreground='#cc0000'
        )
        disclaimer.grid(row=10, column=0, columnspan=4, pady=(5, 0))

    def check_dependencies(self):
        """Check if required dependencies are installed."""
        missing = []
        warnings = []
        
        # Check FFmpeg
        if not is_exe('ffmpeg'):
            missing.append('FFmpeg')
        else:
            if FFMPEG_LOCAL.exists():
                self.log(f"✅ Using local FFmpeg: {FFMPEG_LOCAL}")
            else:
                self.log(f"✅ FFmpeg found in system PATH")
        
        # Check yt-dlp
        if not is_exe('yt-dlp'):
            missing.append('yt-dlp')
        else:
            if shutil.which("yt-dlp"):
                self.log(f"✅ yt-dlp found in PATH")
            else:
                self.log(f"✅ yt-dlp will run as Python module")
        
        # Check spotdl
        if not is_exe('spotdl'):
            missing.append('spotdl')
        else:
            if shutil.which("spotdl"):
                self.log(f"✅ spotdl found in PATH")
            else:
                self.log(f"✅ spotdl will run as Python module")
        
        if missing:
            msg = f"❌ MISSING DEPENDENCIES\n\n"
            msg += f"The following are not installed:\n"
            for item in missing:
                msg += f"  • {item}\n"
            msg += f"\nPlease install missing dependencies:\n"
            msg += f"pip install yt-dlp spotdl mutagen requests\n"
            
            messagebox.showerror("Missing Dependencies", msg)
            self.log(f"❌ Missing: {', '.join(missing)}")
            
            # Disable download buttons
            self.add_button.config(state='disabled')
            self.download_button.config(state='disabled')
            self.status.set("❌ Missing dependencies")
        else:
            self.log("✅ All dependencies are ready!")
            self.status.set("Ready to download")

    def browse_output_dir(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(initialdir=self.output_dir.get())
        if directory:
            self.output_dir.set(directory)
            self.log(f"Output directory changed to: {directory}")

    def log(self, message: str):
        """Add message to log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def update_status(self, text: str):
        """Update status label."""
        self.status.set(text)
        self.root.update_idletasks()

    def on_error(self, msg: str):
        """Handle error."""
        self.status.set(f"❌ Error")
        self.log(f"❌ ERROR: {msg}")
        messagebox.showerror("Error", msg)

    def add_to_queue(self):
        """Add current URL to download queue."""
        url = self.url.get().strip()
        if not url:
            self.on_error("Please enter a valid URL.")
            return
        
        item = {
            'url': url,
            'platform': self.platform.get(),
            'format': self.format.get(),
            'output_dir': self.output_dir.get()
        }
        
        self.download_queue.add(item)
        
        # Add to visual queue
        platform_icon = "🎧" if item['platform'] == "soundcloud" else "🎵"
        format_text = f"[{item['format'].upper()}]"
        self.queue_list.insert(tk.END, f"{platform_icon} {format_text} {url[:60]}...")
        
        self.log(f"Added to queue: {url}")
        self.status.set(f"Queue: {self.download_queue.size()} items")
        
        # Clear URL entry
        self.url.set("")

    def clear_queue(self):
        """Clear download queue."""
        if not self.is_downloading:
            while not self.download_queue.is_empty():
                self.download_queue.get()
            self.queue_list.delete(0, tk.END)
            self.status.set("Queue cleared")
            self.log("Queue cleared")
        else:
            messagebox.showwarning("Warning", "Cannot clear queue while downloading.")

    def start_queue_processing(self):
        """Start processing download queue."""
        if self.is_downloading:
            messagebox.showinfo("Info", "Download already in progress.")
            return
        
        if self.download_queue.is_empty():
            messagebox.showinfo("Info", "Queue is empty. Add URLs first.")
            return
        
        self.is_downloading = True
        self.download_button.config(state='disabled')
        self.add_button.config(state='disabled')
        self.progress.start()
        
        thread = threading.Thread(target=self.process_queue, daemon=True)
        thread.start()

    def process_queue(self):
        """Process all items in queue."""
        total = self.download_queue.size()
        completed = 0
        
        self.log(f"Starting batch download: {total} items")
        
        while not self.download_queue.is_empty():
            item = self.download_queue.get()
            completed += 1
            
            self.update_status(f"Processing {completed}/{total}...")
            self.log(f"\n{'='*60}")
            self.log(f"Processing item {completed}/{total}")
            
            # Remove from visual queue
            self.root.after(0, lambda: self.queue_list.delete(0))
            
            try:
                if item['platform'] == "soundcloud":
                    download_soundcloud(
                        item['url'],
                        item['format'],
                        item['output_dir'],
                        self.update_status,
                        self.on_error,
                        self.log
                    )
                elif item['platform'] == "spotify":
                    download_spotify(
                        item['url'],
                        item['format'],
                        item['output_dir'],
                        self.update_status,
                        self.on_error,
                        self.log
                    )
                elif item['platform'] == "applemusic":
                    download_applemusic(
                        item['url'],
                        item['format'],
                        item['output_dir'],
                        self.update_status,
                        self.on_error,
                        self.log
                    )
            except Exception as e:
                self.log(f"❌ Failed: {str(e)}")
        
        self.progress.stop()
        self.is_downloading = False
        self.download_button.config(state='normal')
        self.add_button.config(state='normal')
        
        self.update_status(f"✅ Completed {completed}/{total} downloads")
        self.log(f"\n{'='*60}")
        self.log(f"✅ Batch download completed: {completed}/{total} successful")
        
        messagebox.showinfo("Complete", f"Downloaded {completed} items successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
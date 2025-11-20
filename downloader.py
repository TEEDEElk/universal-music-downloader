import argparse
import subprocess
import os
import sys
import shutil
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC, TDRC
from mutagen.wave import WAVE
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def is_exe(name: str) -> bool:
    """Check if an executable is available in PATH."""
    return shutil.which(name) is not None

def download_image(url: str, output_path: str) -> bool:
    """Download album art from URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        logger.error(f"Failed to download album art: {e}")
        return False

def get_track_metadata(file_path: str, platform: str) -> Dict:
    """Extract metadata from downloaded file using yt-dlp info."""
    metadata = {
        "title": "",
        "artist": "Unknown Artist",
        "album": "Unknown Album",
        "year": "",
        "artwork_url": None
    }
    
    try:
        # Try to get metadata from yt-dlp info json
        info_file = file_path.replace('.mp3', '.info.json').replace('.wav', '.info.json')
        if os.path.exists(info_file):
            with open(info_file, 'r', encoding='utf-8') as f:
                info = json.load(f)
                metadata['title'] = info.get('title', os.path.basename(file_path))
                metadata['artist'] = info.get('artist') or info.get('uploader', 'Unknown Artist')
                metadata['album'] = info.get('album', 'Unknown Album')
                metadata['year'] = str(info.get('release_year', ''))
                metadata['artwork_url'] = info.get('thumbnail')
    except Exception as e:
        logger.warning(f"Could not extract metadata from info file: {e}")
        # Fallback to filename
        metadata['title'] = os.path.splitext(os.path.basename(file_path))[0]
    
    return metadata

def embed_metadata_mp3(file_path: str, metadata: Dict, artwork_path: Optional[str] = None):
    """Embed metadata into MP3 file."""
    try:
        audio = MP3(file_path, ID3=ID3)
        try:
            audio.add_tags()
        except:
            pass
        
        audio.tags["TIT2"] = TIT2(encoding=3, text=metadata["title"])
        audio.tags["TPE1"] = TPE1(encoding=3, text=metadata["artist"])
        audio.tags["TALB"] = TALB(encoding=3, text=metadata["album"])
        
        if metadata.get("year"):
            audio.tags["TDRC"] = TDRC(encoding=3, text=metadata["year"])
        
        # Embed album art
        if artwork_path and os.path.exists(artwork_path):
            with open(artwork_path, 'rb') as img:
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
        logger.info(f"Embedded metadata into: {file_path}")
    except Exception as e:
        logger.error(f"Failed to embed MP3 metadata: {e}")

def embed_metadata_wav(file_path: str, metadata: Dict):
    """Embed metadata into WAV file."""
    try:
        audio = WAVE(file_path)
        audio["INAM"] = metadata["title"]
        audio["IART"] = metadata["artist"]
        audio["IPRD"] = metadata["album"]
        if metadata.get("year"):
            audio["ICRD"] = metadata["year"]
        audio.save()
        logger.info(f"Embedded metadata into: {file_path}")
    except Exception as e:
        logger.error(f"Failed to embed WAV metadata: {e}")

def download_soundcloud(url: str, output_format: str, output_dir: str = ".") -> List[str]:
    """Download from SoundCloud with metadata and album art."""
    logger.info(f"Downloading from SoundCloud: {url}")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    out_template = str(output_path / "%(title)s.%(ext)s")
    
    # Download with metadata
    args = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", output_format,
        "--audio-quality", "0",  # Best quality
        "--embed-thumbnail",  # Embed artwork
        "--write-info-json",  # Save metadata
        "--add-metadata",  # Add metadata to file
        "--no-playlist",  # Don't download playlists accidentally
        "--ignore-errors",  # Continue on errors
        "--no-overwrites",  # Don't overwrite existing files
        "--continue",  # Resume incomplete downloads
        "-o", out_template,
        url
    ]
    
    if output_format == "mp3":
        args.extend(["--postprocessor-args", "ffmpeg:-b:a 320k -ar 44100"])  # Force 320kbps, 44.1kHz
    
    subprocess.run(args, check=True)
    
    # Find downloaded files
    downloaded_files = []
    for file in output_path.glob(f"*.{output_format}"):
        if file.stat().st_mtime > (os.path.getmtime(output_dir) - 60):  # Recent files
            downloaded_files.append(str(file))
            
            # Download and embed album art
            metadata = get_track_metadata(str(file), "soundcloud")
            if metadata['artwork_url']:
                artwork_path = str(file).replace(f'.{output_format}', '.jpg')
                if download_image(metadata['artwork_url'], artwork_path):
                    if output_format == "mp3":
                        embed_metadata_mp3(str(file), metadata, artwork_path)
                    os.remove(artwork_path)  # Clean up temp artwork
            
            # Clean up info json
            info_file = str(file).replace(f'.{output_format}', '.info.json')
            if os.path.exists(info_file):
                os.remove(info_file)
    
    return downloaded_files

def download_spotify(url: str, output_format: str, output_dir: str = ".") -> List[str]:
    """Download from Spotify with metadata and album art."""
    logger.info(f"Downloading from Spotify: {url}")
    
    if not is_exe('spotdl'):
        logger.error('spotdl is required: pip install spotdl')
        return []
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    original_dir = os.getcwd()
    os.chdir(output_path)
    
    try:
        # spotDL downloads as MP3 with metadata
        cmd = ['spotdl', '--format', 'mp3', '--bitrate', '320k', url]
        subprocess.run(cmd, check=True)
        
        # Find downloaded MP3 files
        downloaded_files = []
        mp3_files = [f for f in os.listdir('.') if f.endswith('.mp3') and 
                     os.path.getmtime(f) > (os.path.getmtime('.') - 60)]
        
        for mp3_file in mp3_files:
            if output_format == "wav":
                # Convert to WAV
                wav_file = mp3_file.replace('.mp3', '.wav')
                subprocess.run([
                    "ffmpeg", "-y", "-i", mp3_file,
                    "-acodec", "pcm_s16le",  # CD quality WAV
                    "-ar", "44100",
                    wav_file
                ], check=True)
                
                # Copy metadata to WAV
                try:
                    mp3_audio = MP3(mp3_file)
                    metadata = {
                        "title": str(mp3_audio.get("TIT2", "")),
                        "artist": str(mp3_audio.get("TPE1", "")),
                        "album": str(mp3_audio.get("TALB", "")),
                        "year": str(mp3_audio.get("TDRC", ""))
                    }
                    embed_metadata_wav(wav_file, metadata)
                except Exception as e:
                    logger.warning(f"Could not transfer metadata to WAV: {e}")
                
                os.remove(mp3_file)  # Remove original MP3
                downloaded_files.append(str(output_path / wav_file))
            else:
                downloaded_files.append(str(output_path / mp3_file))
        
        return downloaded_files
    finally:
        os.chdir(original_dir)

def download_applemusic(url: str, output_format: str, output_dir: str = ".") -> List[str]:
    """Download from Apple Music with metadata and album art."""
    logger.info(f"Downloading from Apple Music: {url}")
    
    if not is_exe('spotdl'):
        logger.error('spotdl is required: pip install spotdl')
        return []
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    original_dir = os.getcwd()
    os.chdir(output_path)
    
    try:
        # spotDL also supports Apple Music URLs
        cmd = ['spotdl', '--format', 'mp3', '--bitrate', '320k', url]
        subprocess.run(cmd, check=True)
        
        # Find downloaded MP3 files
        downloaded_files = []
        mp3_files = [f for f in os.listdir('.') if f.endswith('.mp3') and 
                     os.path.getmtime(f) > (os.path.getmtime('.') - 60)]
        
        for mp3_file in mp3_files:
            if output_format == "wav":
                # Convert to WAV
                wav_file = mp3_file.replace('.mp3', '.wav')
                subprocess.run([
                    "ffmpeg", "-y", "-i", mp3_file,
                    "-acodec", "pcm_s16le",  # CD quality WAV
                    "-ar", "44100",
                    wav_file
                ], check=True)
                
                # Copy metadata to WAV
                try:
                    mp3_audio = MP3(mp3_file)
                    metadata = {
                        "title": str(mp3_audio.get("TIT2", "")),
                        "artist": str(mp3_audio.get("TPE1", "")),
                        "album": str(mp3_audio.get("TALB", "")),
                        "year": str(mp3_audio.get("TDRC", ""))
                    }
                    embed_metadata_wav(wav_file, metadata)
                except Exception as e:
                    logger.warning(f"Could not transfer metadata to WAV: {e}")
                
                os.remove(mp3_file)  # Remove original MP3
                downloaded_files.append(str(output_path / wav_file))
            else:
                downloaded_files.append(str(output_path / mp3_file))
        
        return downloaded_files
    finally:
        os.chdir(original_dir)

def main():
    parser = argparse.ArgumentParser(
        description='Universal Music Track Downloader - SoundCloud, Spotify & Apple Music',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --soundcloud https://soundcloud.com/artist/track --format mp3
  %(prog)s --spotify https://open.spotify.com/track/... --format wav --output ./downloads
  %(prog)s --applemusic https://music.apple.com/us/album/... --format mp3
  
⚠️  For educational purposes only. Respect copyright and platform ToS.
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--soundcloud', help='SoundCloud track/playlist URL')
    group.add_argument('--spotify', help='Spotify track/album/playlist URL')
    group.add_argument('--applemusic', help='Apple Music track/album/playlist URL')
    
    parser.add_argument('--format', choices=['mp3', 'wav'], required=True,
                        help='Output format: mp3 (320kbps) or wav (lossless)')
    parser.add_argument('--output', default='.',
                        help='Output directory for downloaded files (default: current directory)')
    
    args = parser.parse_args()

    # Check dependencies
    if not is_exe('ffmpeg'):
        logger.error('ffmpeg not found! Please install it from https://ffmpeg.org/')
        sys.exit(1)
    if not is_exe('yt-dlp'):
        logger.error('yt-dlp not found! Install: pip install yt-dlp')
        sys.exit(1)

    try:
        downloaded = []
        if args.soundcloud:
            downloaded = download_soundcloud(args.soundcloud, args.format, args.output)
        elif args.spotify:
            downloaded = download_spotify(args.spotify, args.format, args.output)
        elif args.applemusic:
            downloaded = download_applemusic(args.applemusic, args.format, args.output)
        
        if downloaded:
            logger.info(f"\n✅ Successfully downloaded {len(downloaded)} file(s):")
            for file in downloaded:
                logger.info(f"  • {file}")
        else:
            logger.warning("No files were downloaded.")
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Download failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
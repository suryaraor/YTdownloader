import os
import sys
import argparse
import pyperclip
from yt_dlp import YoutubeDL
from datetime import datetime
from typing import Optional

def download_video_for_davinci(url: Optional[str] = None, save_path: str = ".", info_only: bool = False, cookiefile: Optional[str] = None) -> None:
    try:
        # If a URL wasn't provided, try the clipboard
        if not url:
            url = pyperclip.paste().strip()
        if not url or not url.startswith("http"):
            raise ValueError("No valid URL provided. Pass a YouTube URL as the first argument or copy one to the clipboard.")

        print(f"🎥 Downloading from: {url}")

        # Get today's date in yyyy-mm-dd format for organized saving
        today_date = datetime.now().strftime('%Y-%m-%d')
        video_path = os.path.join(save_path, today_date, "Videos")
        audio_path = os.path.join(save_path, today_date, "Audio")

        # Create folders if they do not exist
        os.makedirs(video_path, exist_ok=True)
        os.makedirs(audio_path, exist_ok=True)

        print(f"📂 Saving MP4 in: {video_path}")
        print(f"🎵 Saving MP3 in: {audio_path}")

    # Options for downloading video in DaVinci-compatible format (MP4)
        video_options = {
            'outtmpl': os.path.join(video_path, '%(title)s.%(ext)s'),  # Save as title.mp4
            # Prefer combined best video+audio (DASH) with fallbacks; keep headers and retries
            'format': 'bestvideo+bestaudio/best',  # prefer separate best video+audio then fallback to best
            # Disable resumed downloads to avoid range/resume 403 issues
            'continuedl': False,
            # Bind to an IPv4 address where helpful (may avoid some network 403s)
            'source_address': '0.0.0.0',
            # Skip unavailable fragments rather than failing immediately
            'skip_unavailable_fragments': True,
            # Prefer native HLS handling as fallback
            'hls_prefer_native': True,
            'hls_use_mpegts': True,
            'merge_output_format': 'mp4',
            # Set browser-like headers to reduce blocking from YouTube
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            # Retry settings
            'retries': 10,
            'noprogress': False,
            'quiet': False,
            'progress_hooks': [lambda d: print(f"📥 Video status: {d['status']}") if d['status'] == 'downloading' else None],
        }

        # If a cookies file was provided, add it to options
        if cookiefile:
            video_options['cookiefile'] = cookiefile

        # Options for downloading audio-only format (MP3)
        audio_options = {
            'outtmpl': os.path.join(audio_path, '%(title)s.%(ext)s'),  # Save as title.mp3
            'format': 'bestaudio/best',  # Best quality audio
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            'retries': 10,
            'noprogress': False,
            'quiet': False,
            'progress_hooks': [lambda d: print(f"🎶 Audio status: {d['status']}") if d['status'] == 'downloading' else None],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        if cookiefile:
            audio_options['cookiefile'] = cookiefile

        # If user requested info-only, extract metadata without downloading
        if info_only:
            with YoutubeDL({'quiet': False}) as ydl:
                info = ydl.extract_info(url, download=False)
                print("ℹ️  Video info extracted (info-only mode). Title:", info.get('title'))
                return

        # Download video
        with YoutubeDL(video_options) as ydl:
            ydl.download([url])
            print("✅ MP4 Download Completed!")

        # Download audio
        with YoutubeDL(audio_options) as ydl:
            ydl.download([url])
            print("✅ MP3 Download Completed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        # Propagate non-zero exit status when used as a script
        raise

# Run the function
if __name__ == "__main__":
    # Allow passing the URL as a command-line argument: `py youtube.py <URL>`
    arg_url = None
    # Determine if info-only mode was requested
    info_mode = '--info' in sys.argv
    # First non-flag argument is treated as URL (if present)
    arg_url = None
    for a in sys.argv[1:]:
        if a == '--info':
            continue
        arg_url = a
        break
    try:
        download_video_for_davinci(url=arg_url, info_only=info_mode)
    except Exception:
        # Exit with non-zero code so callers can detect failure
        sys.exit(1)

import os
import subprocess

import yt_dlp

# List of URLs of YouTube videos
urls = [
"https://www.youtube.com/shorts/iPCzhTjTLWw",
"https://www.youtube.com/shorts/InTN1yaMDHE",
"https://www.youtube.com/shorts/DQqLaSK-LnI",
"https://www.youtube.com/shorts/foPMXTJQA7Y"

]

def convert_webm_to_mp3(file_path):
    if not file_path or not file_path.lower().endswith(".webm"):
        return

    mp3_path = os.path.splitext(file_path)[0] + ".mp3"
    if os.path.exists(mp3_path):
        print(f"[convert] MP3 already exists: {mp3_path}")
        return

    try:
        # Convert only audio stream to MP3 while keeping the original WEBM file.
        subprocess.run(
            ["ffmpeg", "-y", "-i", file_path, "-vn", "-codec:a", "libmp3lame", "-q:a", "2", mp3_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        print(f"[convert] Created MP3: {mp3_path}")
    except FileNotFoundError:
        print("[convert] ffmpeg is not installed or not in PATH; skipping MP3 conversion.")
    except subprocess.CalledProcessError:
        print(f"[convert] Failed to convert: {file_path}")


def convert_mkv_to_mp4(file_path):
    if not file_path or not file_path.lower().endswith(".mkv"):
        return

    mp4_path = os.path.splitext(file_path)[0] + ".mp4"
    if os.path.exists(mp4_path):
        print(f"[convert] MP4 already exists: {mp4_path}")
        return

    try:
        # Copy audio/video streams into MP4 container without re-encoding.
        subprocess.run(
            ["ffmpeg", "-y", "-i", file_path, "-c", "copy", mp4_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        print(f"[convert] Created MP4: {mp4_path}")
    except FileNotFoundError:
        print("[convert] ffmpeg is not installed or not in PATH; skipping MP4 conversion.")
    except subprocess.CalledProcessError:
        print(f"[convert] Failed to convert: {file_path}")


def iter_entries(info):
    if not info:
        return

    entries = info.get("entries")
    if entries:
        for entry in entries:
            yield from iter_entries(entry)
    else:
        yield info


# Download the videos and convert WEBM outputs to MP3 as well.
ydl_opts = {}
mkv_outputs = set()
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    for url in urls:
        info = ydl.extract_info(url, download=True)
        for entry in iter_entries(info):
            file_path = entry.get("filepath") or entry.get("_filename")
            if not file_path:
                file_path = ydl.prepare_filename(entry)
            convert_webm_to_mp3(file_path)

            if file_path and file_path.lower().endswith(".mkv"):
                mkv_outputs.add(file_path)

            for download_item in entry.get("requested_downloads", []):
                dl_path = download_item.get("filepath")
                if dl_path and dl_path.lower().endswith(".mkv"):
                    mkv_outputs.add(dl_path)

# At the end of the process, convert any MKV outputs to MP4 as well.
for mkv_file in sorted(mkv_outputs):
    convert_mkv_to_mp4(mkv_file)

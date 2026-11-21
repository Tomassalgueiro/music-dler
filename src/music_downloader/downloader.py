from pathlib import Path
from urllib.parse import urlparse
import yt_dlp

DIRECT_AUDIO_EXTS = { ".mp3", ".flac", ".wav", ".m4a", ".ogg", ".opus", ".zip" }

def detect_source(url: str) -> str:
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    path = parsed.path.lower()

    if "spotify.com" in domain: 
        return "spotify"
    if any(path.endswith(ext) for ext in DIRECT_AUDIO_EXTS):
        return "direct_file"
    return "ytdlp"

def build_ydl_options(output_dir: str, audio_format: str = "mp3", split_chapters: bool = False, progress_hook = None, split_chapters: bool = False) -> dict:

    base_dir = Path(output_dir).expanduser().resolve()

    postprocessors = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_format,
                "preferredquality": "0",
            },
            {"key": "FFmpegMetadata"},
            {"key": "EmbedThumbnail"},
    ]

    outtmpl = {
            "default": str(base_dir / "%(artist,uploader)s" / "%(album,playlist_title|Singles)s" / "%(title)s.%(ext)s"),
    }

    ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": outtmpl,
            "writethumbnail": True,
            "postprocessors": postprocessors,
            "ignoreerrors": True,
            "quiet": True,
            "no_warnings": True,
            "split_chapters": split_chapters,
            "progress_hooks": [progress_hook] if progress_hook else []
            }
    
    return ydl_opts

def download_with_ytdlp(url: str, options: dict) -> bool:

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"Download error for {url}: {e}")
        return False

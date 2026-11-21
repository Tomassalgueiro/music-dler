import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests
import yt_dlp
from bs4 import BeautifulSoup
from mutagen import File as MutagenFile

DIRECT_AUDIO_EXTS = { ".mp3", ".flac", ".wav", ".m4a", ".ogg", ".opus"}
ARCHIVE_EXTS = { ".zip" }

def sanitize(name:str) -> str:
    return "".join(c for c in name if c not in r'\/:*?"<>|').strip() or "Unknown"

def detect_source(url: str) -> str:
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    path = parsed.path.lower()

    if "spotify.com" in domain: 
        return "spotify"
    if any(path.endswith(ext) for ext in DIRECT_AUDIO_EXTS | ARCHIVE_EXTS):
        return "direct_file" 
    return "ytdlp"

def build_ydl_options(output_dir: str, audio_format: str = "mp3", split_chapters: bool = False, progress_hook = None) -> dict:

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

    if split_chapters:
        postprocessors.append({"key": "FFmpegSplitChapters", "force_keyframes": False})
        outtmpl["chapter"] = str(
            base_dir / "%(artist,uploader)s" / "%(title)s" / "%(section_number)02d - %(section_title)s.%(ext)s"
        )

    return {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "writethumbnail": True,
        "postprocessors": postprocessors,
        "ignoreerrors": True,
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [progress_hook] if progress_hook else [],
    }


def download_with_ytdlp(url: str, options: dict) -> bool:

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"Download error for {url}: {e}")
        return False

def extract_spotify_queries(spotify_url: str) -> list[str]:
    parsed = urlparse(spotify_url)
    embed_url = f"https://open.spotify.com/embed{parsed.path}"

    resp = requests.get(embed_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    script_tag = soup.find("script", id="__NEXT_DATA__")
    if not script_tag or not script_tag.string:
        return []

    data = json.loads(script_tag.string)
    entity = data.get("props", {}).get("pageProps", {}).get("state", {}).get("data", {}).get("entity", {})

    queries = []
    if entity.get("type") == "track":
        title = entity.get("name", "")
        artists = ", ".join(a.get("name", "") for a in entity.get("artists", []))
        if title:
            queries.append(f"ytsearch1:{artists} - {title} audio")

    elif "trackList" in entity:
        for track in entity["trackList"]:
            title = track.get("title", "")
            subtitle = track.get("subtitle", "")
            if title:
                queries.append(f"ytsearch1:{subtitle} - {title} audio")

    return queries

def download_spotify(url: str, options: dict) -> bool:

    try:
        queries = extract_spotify_queries(url)
        if not queries:
            print(f"Could not extract from url: {url}")
            return False
        
        all_ok = True
        for q in queries:
            ok = download_with_ytdlp(q, options)
            if not ok:
                all_ok = False
        return all_ok
    except Exception as e:
        print(f"Spotify error for {url}: {e}")
        return False

def _sort_direct_track(filepath: Path, base_dir: Path) -> Path:
    audio = MutagenFile(filepath, easy=True)
    artist = sanitize(audio.get("artist", ["Unknown Artist"])[0]) if audio else "Unknown Artist"
    album = sanitize(audio.get("album", ["Singles"])[0]) if audio else "Singles"

    target_dir = base_dir / artist / album
    target_dir.mkdir(parents=True, exist_ok=True)
    dest = target_dir / filepath.name
    shutil.move(str(filepath), str(dest))
    return dest


def download_direct_file(url: str, output_dir: str) -> bool:
    base_dir = Path(output_dir).expanduser().resolve()

    try:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            with requests.get(url, stream=True, timeout=20) as r:
                r.raise_for_status()
                filename = unquote(Path(urlparse(url).path).name) or "download.bin"
                downloaded = tmp_path / filename

                with open(downloaded, "wb") as f:
                    for chunk in r.iter_content(chunk_size=16384):
                        f.write(chunk)

            if downloaded.suffix.lower() == ".zip":
                extract_dir = tmp_path / "extracted"
                with zipfile.ZipFile(downloaded, "r") as z:
                    z.extractall(extract_dir)
                for item in extract_dir.rglob("*"):
                    if item.suffix.lower() in DIRECT_AUDIO_EXTS:
                        _sort_direct_track(item, base_dir)
                return True

            if downloaded.suffix.lower() in DIRECT_AUDIO_EXTS:
                _sort_direct_track(downloaded, base_dir)
                return True

            return False
    except Exception as e:
        print(f"Direct download error for {url}: {e}")
        return False

def process_link(url:str, output_dir: str, audio_format: str = "mp3", split_chapters: bool = False, progress_hook = None) -> bool:

    source = detect_source(url)

    if source == "direct_file":
        return download_direct_file(url, output_dir)

    options = build_ydl_options(
            output_dir=output_dir,
            audio_format=audio_format,
            split_chapters=split_chapters,
            progress_hook=progress_hook,
            )

    if source == "spotify":
        return download_spotify(url,options)

    return download_with_ytdlp(url, options)

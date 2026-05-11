import os
import shutil
import yt_dlp
import aiohttp
import asyncio
from io import BytesIO
from PIL import Image

from deno_runtime import get_deno
from settings_manager import get_cookies_path, get_downloads_dir


VIDEO_DIR = get_downloads_dir()

MAX_FILE_SIZE_BYTES = 1950 * 1024 * 1024  # ~1.95 GB


def get_ydl_options(download=False, progress_callback=None):
    """
    Returns yt-dlp settings.
    Based on RKGDTUBE bot implementation.
    """
    # JS runtimes for signature solving
    deno = get_deno()
    js_runtimes = {}
    if deno.is_available:
        js_runtimes['deno'] = {}

    options = {
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'check_hostname': False,
        'js_runtimes': js_runtimes if js_runtimes else None,
        'remote_components': ['ejs:github'],
        'http_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
        },
        'extractor_args': {
            'youtube': {
                'include_dash_manifest': True,
                'include_hls_manifest': True,
                'player_skip': ['web_embedded'],
            },
            'youtubetab': {
                'skip': ['authcheck']
            }
        },
        'format_sort': ['vcodec:h264', 'res:1080', 'ext:mp4:m4a'],
        'merge_output_format': 'mp4',
        'hls_prefer_native': False,
        'socket_timeout': 120,
        'retries': 10,
        'fragment_retries': 10,
        'allow_unplayable_formats': False,
        'check_formats': False,
        'prefer_free_formats': False,
        'ignoreerrors': True,
        'no_color': True,
        'no_cache_dir': True,
        'buffer_size': 1024 * 16,
    }

    # Cookies from settings
    cookies_path = get_cookies_path()
    if cookies_path and os.path.exists(cookies_path):
        options['cookiefile'] = cookies_path

    if not download:
        return options

    # Download settings
    options.update({
        'extract_flat': False,
        'ignoreerrors': False,
        'nopart': False,
        'max_filesize': MAX_FILE_SIZE_BYTES,
        'format_sort': ['res:1080', 'vcodec:h264', 'ext:mp4:m4a'],
        'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best',
    })

    if progress_callback:
        options['progress_hooks'] = [progress_callback]

    return options


def get_video_info(url: str) -> dict:
    """Gets YouTube video metadata without downloading."""
    ydl_opts = get_ydl_options(download=False)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    if not info:
        raise RuntimeError("Could not extract video information.")

    return {
        'title': info.get('title', 'No title'),
        'uploader': info.get('uploader', 'Unknown Uploader'),
        'description': info.get('description', ''),
        'thumbnail': info.get('thumbnail', None),
        'duration': info.get('duration', 0),
        'width': info.get('width', 1920),
        'height': info.get('height', 1080),
        'url': info.get('webpage_url', url),
    }


def download_video(url: str, output_path: str, progress_callback=None):
    """
    Downloads YouTube video in maximum quality up to 1080p H264 MP4.
    Uses the same approach as the RKGDTUBE bot.
    """
    def progress_hook(d):
        if progress_callback and d['status'] == 'downloading':
            progress_callback({
                'status': 'downloading',
                'downloaded_bytes': d.get('downloaded_bytes', 0),
                'total_bytes': d.get('total_bytes') or d.get('total_bytes_estimate', 0),
                'speed': d.get('speed', 0),
                'eta': d.get('eta', 0),
                'percent': d.get('downloaded_bytes', 0) / (d.get('total_bytes') or d.get('total_bytes_estimate', 1)) * 100
                if d.get('total_bytes') or d.get('total_bytes_estimate') else 0
            })
        elif progress_callback and d['status'] == 'finished':
            progress_callback({
                'status': 'finished',
                'downloaded_bytes': d.get('downloaded_bytes', 0),
                'total_bytes': d.get('total_bytes', 0),
                'percent': 100
            })

    ydl_opts = get_ydl_options(download=True, progress_callback=progress_hook)
    ydl_opts['outtmpl'] = output_path

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        meta = ydl.extract_info(url, download=True)

    if meta is None:
        raise RuntimeError("Download failed: no metadata returned.")

    # Determine actual file path (yt-dlp may change extension after merge)
    filename = ydl.prepare_filename(meta)
    actual_path = filename

    if not os.path.exists(actual_path):
        base_path = os.path.splitext(filename)[0]
        for ext in ['.mp4', '.mkv', '.webm']:
            candidate = base_path + ext
            if os.path.exists(candidate):
                actual_path = candidate
                break

    # Ensure final file is at output_path
    if actual_path != output_path and os.path.exists(actual_path):
        if os.path.exists(output_path):
            os.remove(output_path)
        os.rename(actual_path, output_path)

    if not os.path.exists(output_path):
        raise FileNotFoundError("Video file was not created.")

    if os.path.getsize(output_path) <= 0:
        raise RuntimeError("Video file is empty.")

    return output_path


async def download_thumbnail(thumbnail_url: str, output_path: str = None):
    """
    Downloads thumbnail and resizes to 320x320.
    """
    if not thumbnail_url:
        return None

    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail_url) as response:
            if response.status == 200:
                data = await response.read()
                image = Image.open(BytesIO(data)).convert('RGB')

                if image.width > 320 or image.height > 320:
                    image.thumbnail((320, 320))

                if output_path:
                    image.save(output_path, format='JPEG')
                    return output_path
                else:
                    buffer = BytesIO()
                    image.save(buffer, format='JPEG')
                    buffer.seek(0)
                    return buffer
            else:
                return None


def get_download_path(url_hash: str) -> str:
    """Returns path for downloading video."""
    return os.path.join(VIDEO_DIR, f"video_{url_hash}.mp4")


def get_thumbnail_path(url_hash: str) -> str:
    """Returns path for thumbnail."""
    return os.path.join(VIDEO_DIR, f"thumb_{url_hash}.jpg")


def cleanup_files(url_hash: str):
    """Deletes downloaded files."""
    video_path = get_download_path(url_hash)
    thumb_path = get_thumbnail_path(url_hash)

    for path in [video_path, thumb_path]:
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass


import yt_dlp
import asyncio
import logging
import re
import tempfile
import os
import base64

logger = logging.getLogger(__name__)

_COOKIES_PATH = None

def _ensure_cookies_file():
    global _COOKIES_PATH
    if _COOKIES_PATH:
        return _COOKIES_PATH
    b64 = os.environ.get("YTDLP_COOKIES_B64")
    if not b64:
        return None
    try:
        data = base64.b64decode(b64)
        tmpdir = tempfile.gettempdir()
        path = os.path.join(tmpdir, "yt_cookies.txt")
        with open(path, "wb") as f:
            f.write(data)
        _COOKIES_PATH = path
        logger.info(f"yt-dlp cookies written to {path}")
        return _COOKIES_PATH
    except Exception as e:
        logger.error(f"Failed to decode/write cookies: {e}")
        return None

def is_youtube_url(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    return re.match(youtube_regex, url)

def get_video_metadata(url):
    if not is_youtube_url(url):
        return {"error": "Invalid YouTube URL"}

    cookies = _ensure_cookies_file()
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'format': 'bestaudio/best',
        'extractor_args': {
            'youtube': {
                'player_client': ['android']
            }
        },
    }
    if cookies:
        ydl_opts['cookiefile'] = cookies
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title", "video"),
                "author": info.get("uploader", "unknown"),
                "thumbnail": info.get("thumbnail"),
                "formats": [{
                    "format_id": f.get("format_id"),
                    "ext": f.get("ext"),
                    "acodec": f.get("acodec"),
                    "vcodec": f.get("vcodec"),
                    "abr": f.get("abr"),
                    "language": f.get("language")
                } for f in info.get("formats", [])],
                "language": info.get("language"),
            }
        except yt_dlp.utils.DownloadError as e:
            return {"error": str(e)}

async def stream_audio(url, format_id, convert_to_mp3, progress_cb=None):
    # Create a temporary directory in the system temp (works locally and in Docker)
    temp_dir = tempfile.mkdtemp()
    raw_audio_filepath = os.path.join(temp_dir, "raw_audio")

    # Arguments for yt-dlp to download the raw audio stream
    yt_dlp_args = [
        'yt-dlp',
        '--no-part',
        '--extractor-args', 'youtube:player_client=android',
        '--format', format_id,
        '-o', f"{raw_audio_filepath}.%(ext)s",
        url
    ]
    cookies = _ensure_cookies_file()
    if cookies:
        yt_dlp_args[1:1] = ['--cookies', cookies]
    
    logger.info(f"Executing yt-dlp command for raw download: {' '.join(yt_dlp_args)}")
    if progress_cb:
        progress_cb("downloading", None)

    # Execute yt-dlp to download the raw audio
    yt_dlp_proc = await asyncio.create_subprocess_exec(
        *yt_dlp_args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    await yt_dlp_proc.wait()

    if yt_dlp_proc.returncode != 0:
        stderr = await yt_dlp_proc.stderr.read()
        logger.error(f"yt-dlp raw download failed (return code {yt_dlp_proc.returncode}): {stderr.decode(errors='ignore')}")
        # best-effort cleanup
        try:
            for name in os.listdir(temp_dir):
                try:
                    os.remove(os.path.join(temp_dir, name))
                except Exception:
                    pass
            os.rmdir(temp_dir)
        except Exception:
            pass
        raise Exception("Failed to download raw audio")

    # Determine actual downloaded file path (with extension)
    try:
        candidates = [
            os.path.join(temp_dir, name)
            for name in os.listdir(temp_dir)
            if name.startswith("raw_audio.") and not name.endswith(".part")
        ]
    except Exception:
        candidates = []

    if not candidates:
        # Read and log stderr for debugging
        stderr = await yt_dlp_proc.stderr.read()
        logger.error(f"yt-dlp produced no output file. Stderr: {stderr.decode(errors='ignore')}")
        os.rmdir(temp_dir)
        raise Exception("Failed to download audio: output file not found")

    # Use the first candidate (yt-dlp should produce a single file for the chosen format)
    raw_audio_file_with_ext = candidates[0]

    if progress_cb:
        progress_cb("download_complete", os.path.basename(raw_audio_file_with_ext))

    # Check raw audio file size
    raw_file_size = os.path.getsize(raw_audio_file_with_ext)
    logger.info(f"Raw audio file created: {raw_audio_file_with_ext}, size: {raw_file_size} bytes")
    max_file_size_mb = 100  # 100 MB limit
    if raw_file_size > max_file_size_mb * 1024 * 1024:
        os.remove(raw_audio_file_with_ext) # Clean up large file
        os.rmdir(temp_dir) # Clean up the temporary directory
        raise Exception(f"Downloaded raw file size ({raw_file_size / (1024 * 1024):.2f} MB) exceeds the limit of {max_file_size_mb} MB.")

    if convert_to_mp3:
        # Create a temporary file for the MP3 output
        mp3_filepath = os.path.join(temp_dir, "converted_audio.mp3")

        # Arguments for ffmpeg conversion
        ffmpeg_args = [
            'ffmpeg',
            '-i', raw_audio_file_with_ext,
            '-vn', # No video
            '-ab', '192k', # Audio bitrate
            '-map_metadata', '0', # Copy metadata
            mp3_filepath
        ]

        logger.info(f"Executing ffmpeg command: {' '.join(ffmpeg_args)}")
        if progress_cb:
            progress_cb("converting", None)

        # Execute ffmpeg to convert to MP3
        ffmpeg_proc = await asyncio.create_subprocess_exec(
            *ffmpeg_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        await ffmpeg_proc.wait()

        if ffmpeg_proc.returncode != 0:
            stderr = await ffmpeg_proc.stderr.read()
            logger.error(f"ffmpeg conversion failed (return code {ffmpeg_proc.returncode}): {stderr.decode()}")
            if os.path.exists(raw_audio_file_with_ext):
                os.remove(raw_audio_file_with_ext)
            if os.path.exists(mp3_filepath):
                os.remove(mp3_filepath)
            os.rmdir(temp_dir) # Clean up the temporary directory
            raise Exception("Failed to convert audio to MP3")

        # Stream the converted MP3 file
        with open(mp3_filepath, 'rb') as f:
            if progress_cb:
                progress_cb("streaming", "mp3")
            while True:
                chunk = f.read(1024 * 64) # 64KB chunks
                if not chunk:
                    break
                yield chunk

        # Clean up temporary files
        os.remove(raw_audio_file_with_ext)
        os.remove(mp3_filepath)
        os.rmdir(temp_dir) # Clean up the temporary directory
        if progress_cb:
            progress_cb("completed", None)

    else: # Stream the raw audio directly
        with open(raw_audio_file_with_ext, 'rb') as f:
            if progress_cb:
                progress_cb("streaming", os.path.splitext(raw_audio_file_with_ext)[1].lstrip('.'))
            while True:
                chunk = f.read(1024 * 64) # 64KB chunks
                if not chunk:
                    break
                yield chunk
        
        # Clean up the raw audio file
        os.remove(raw_audio_file_with_ext)
        os.rmdir(temp_dir) # Clean up the temporary directory
        if progress_cb:
            progress_cb("completed", None)


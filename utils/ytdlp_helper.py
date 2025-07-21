
import yt_dlp
import asyncio
import logging
import re
import tempfile
import os

logger = logging.getLogger(__name__)

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

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'format': 'bestaudio/best',
    }
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
                    "abr": f.get("abr"),
                    "language": f.get("language")
                } for f in info.get("formats", [])],
                "language": info.get("language"),
            }
        except yt_dlp.utils.DownloadError as e:
            return {"error": str(e)}

async def stream_audio(url, format_id, convert_to_mp3):
    # Create a temporary directory within /app
    temp_dir = tempfile.mkdtemp(dir="/app")
    raw_audio_filepath = os.path.join(temp_dir, "raw_audio")

    # Arguments for yt-dlp to download the raw audio stream
    yt_dlp_args = [
        'yt-dlp',
        '--format', format_id,
        '-o', raw_audio_filepath,
        url
    ]
    
    logger.info(f"Executing yt-dlp command for raw download: {' '.join(yt_dlp_args)}")

    # Execute yt-dlp to download the raw audio
    yt_dlp_proc = await asyncio.create_subprocess_exec(
        *yt_dlp_args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    await yt_dlp_proc.wait()

    if yt_dlp_proc.returncode != 0:
        stderr = await yt_dlp_proc.stderr.read()
        logger.error(f"yt-dlp raw download failed (return code {yt_dlp_proc.returncode}): {stderr.decode()}")
        if os.path.exists(raw_audio_filepath):
            os.remove(raw_audio_filepath)
        os.rmdir(temp_dir) # Clean up the temporary directory
        raise Exception("Failed to download raw audio")

    # Check raw audio file size
    raw_file_size = os.path.getsize(raw_audio_filepath)
    logger.info(f"Raw audio file created: {raw_audio_filepath}, size: {raw_file_size} bytes")
    max_file_size_mb = 100  # 100 MB limit
    if raw_file_size > max_file_size_mb * 1024 * 1024:
        os.remove(raw_audio_filepath) # Clean up large file
        os.rmdir(temp_dir) # Clean up the temporary directory
        raise Exception(f"Downloaded raw file size ({raw_file_size / (1024 * 1024):.2f} MB) exceeds the limit of {max_file_size_mb} MB.")

    if convert_to_mp3:
        # Create a temporary file for the MP3 output
        mp3_filepath = os.path.join(temp_dir, "converted_audio.mp3")

        # Arguments for ffmpeg conversion
        ffmpeg_args = [
            'ffmpeg',
            '-i', raw_audio_filepath,
            '-vn', # No video
            '-ab', '192k', # Audio bitrate
            '-map_metadata', '0', # Copy metadata
            mp3_filepath
        ]

        logger.info(f"Executing ffmpeg command: {' '.join(ffmpeg_args)}")

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
            if os.path.exists(raw_audio_filepath):
                os.remove(raw_audio_filepath)
            if os.path.exists(mp3_filepath):
                os.remove(mp3_filepath)
            os.rmdir(temp_dir) # Clean up the temporary directory
            raise Exception("Failed to convert audio to MP3")

        # Stream the converted MP3 file
        with open(mp3_filepath, 'rb') as f:
            while True:
                chunk = f.read(1024 * 64) # 64KB chunks
                if not chunk:
                    break
                yield chunk

        # Clean up temporary files
        os.remove(raw_audio_filepath)
        os.remove(mp3_filepath)
        os.rmdir(temp_dir) # Clean up the temporary directory

    else: # Stream the raw audio directly
        with open(raw_audio_filepath, 'rb') as f:
            while True:
                chunk = f.read(1024 * 64) # 64KB chunks
                if not chunk:
                    break
                yield chunk
        
        # Clean up the raw audio file
        os.remove(raw_audio_filepath)
        os.rmdir(temp_dir) # Clean up the temporary directory


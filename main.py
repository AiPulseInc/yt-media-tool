import logging
import os
from fastapi import FastAPI, Request, Query, HTTPException, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from utils.ytdlp_helper import get_video_metadata, stream_audio
import shutil
import uuid
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory progress store; for demo/MVP only.
PROGRESS: Dict[str, Dict[str, Any]] = {}

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.get("/metadata")
def metadata(url: str = Query(..., max_length=2048)):
    logger.info(f"Received metadata request for URL: {url}")
    data = get_video_metadata(url)
    logger.info(f"Returning metadata: {data}")
    
    # Save metadata to data.json for debugging
    import json
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    if "error" in data:
        raise HTTPException(status_code=400, detail=data["error"])
    return data

@app.post("/download")
async def download(request: Request):
    data = await request.json()
    url = data.get("url")
    format_id = data.get("format_id")
    convert_to_mp3 = data.get("convert_to_mp3", False)
    task_id = data.get("task_id") or str(uuid.uuid4())

    if not url or not format_id:
        raise HTTPException(status_code=400, detail="URL and format_id are required.")

    # Basic URL length validation
    if len(url) > 2048:
        raise HTTPException(status_code=400, detail="URL is too long.")
    
    metadata = get_video_metadata(url)
    video_title = metadata.get("title", "audio")
    safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-')).rstrip()

    # Determine the correct file extension based on the selected format
    selected_format_info = next((f for f in metadata.get("formats", []) if f.get("format_id") == format_id), None)
    file_extension = selected_format_info.get("ext", "mp3") if selected_format_info else "mp3"

    if convert_to_mp3:
        file_extension = "mp3"

    # Register task and preflight dependency checks to avoid generator crashes that surface as fetch network errors on the client
    PROGRESS[task_id] = {"stage": "initializing", "detail": None}
    if shutil.which('yt-dlp') is None:
        PROGRESS[task_id] = {"stage": "error", "detail": "yt-dlp not on PATH"}
        raise HTTPException(status_code=500, detail="yt-dlp is not available on the server PATH. Ensure dependencies are installed in the current environment.")

    if convert_to_mp3 and shutil.which('ffmpeg') is None:
        PROGRESS[task_id] = {"stage": "error", "detail": "ffmpeg not on PATH"}
        raise HTTPException(status_code=400, detail="ffmpeg is not installed or not on PATH. Install ffmpeg or uncheck 'Konwertuj do MP3'.")

    headers = {
        'Content-Disposition': f'attachment; filename="{safe_title}.{file_extension}"'
    }

    # Choose proper media type
    media_type_map = {
        'mp3': 'audio/mpeg',
        'm4a': 'audio/mp4',
        'mp4': 'audio/mp4',
        'webm': 'audio/webm',
        'ogg': 'audio/ogg',
        'opus': 'audio/ogg'
    }
    media_type = media_type_map.get(file_extension.lower(), 'application/octet-stream')
    
    def progress_cb(stage: str, detail: str | None = None):
        PROGRESS[task_id] = {"stage": stage, "detail": detail}

    try:
        PROGRESS[task_id] = {"stage": "starting_download", "detail": None}
        response = StreamingResponse(
            stream_audio(url, format_id, convert_to_mp3, progress_cb),
            headers={**headers, 'X-Task-Id': task_id},
            media_type=media_type
        )
        return response
    except Exception as e:
        logger.error(f"Error during audio streaming: {e}")
        PROGRESS[task_id] = {"stage": "error", "detail": str(e)}
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/progress")
def progress(task_id: str = Query(...)):
    data = PROGRESS.get(task_id)
    if not data:
        raise HTTPException(status_code=404, detail="Unknown task")
    return {"task_id": task_id, **data}

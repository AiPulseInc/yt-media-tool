import logging
from fastapi import FastAPI, Request, Query, HTTPException, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from utils.ytdlp_helper import get_video_metadata, stream_audio

from redis.asyncio import Redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

async def startup_event():
    redis_host = os.environ.get("REDIS_HOST", "redis")
    redis_port = int(os.environ.get("REDIS_PORT", 6379))
    redis = Redis(host=redis_host, port=redis_port, db=0)
    await FastAPILimiter.init(redis)

app.add_event_handler("startup", startup_event)

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.get("/metadata", dependencies=[Depends(RateLimiter(times=5, seconds=10))])
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

@app.post("/download", dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def download(request: Request):
    data = await request.json()
    url = data.get("url")
    format_id = data.get("format_id")
    convert_to_mp3 = data.get("convert_to_mp3", False)

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

    headers = {
        'Content-Disposition': f'attachment; filename="{safe_title}.{file_extension}"'
    }
    
    try:
        return StreamingResponse(stream_audio(url, format_id, convert_to_mp3), headers=headers, media_type="audio/mpeg")
    except Exception as e:
        logger.error(f"Error during audio streaming: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

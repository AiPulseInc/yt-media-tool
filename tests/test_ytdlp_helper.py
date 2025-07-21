import pytest
from unittest.mock import patch
import yt_dlp
from utils.ytdlp_helper import is_youtube_url, get_video_metadata

def test_is_youtube_url():
    assert is_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is not None
    assert is_youtube_url("https://youtu.be/dQw4w9WgXcQ") is not None
    assert is_youtube_url("https://www.youtube.com/embed/dQw4w9WgXcQ") is not None
    assert is_youtube_url("https://www.google.com") is None
    assert is_youtube_url("invalid-url") is None

@patch('utils.ytdlp_helper.is_youtube_url', return_value=True)
@patch('yt_dlp.YoutubeDL')
def test_get_video_metadata_success(mock_youtube_dl, mock_is_youtube_url):
    mock_instance = mock_youtube_dl.return_value.__enter__.return_value
    mock_instance.extract_info.return_value = {
        "title": "Test Video",
        "uploader": "Test Uploader",
        "thumbnail": "http://example.com/thumb.jpg",
        "formats": [
            {"format_id": "140", "ext": "m4a", "acodec": "mp4a.40.2", "abr": 128},
            {"format_id": "251", "ext": "webm", "acodec": "opus", "abr": 160},
        ],
    }
    
    metadata = get_video_metadata("https://www.youtube.com/watch?v=test")
    assert metadata["title"] == "Test Video"
    assert metadata["author"] == "Test Uploader"
    assert metadata["thumbnail"] == "http://example.com/thumb.jpg"
    assert len(metadata["formats"]) == 2

@patch('yt_dlp.YoutubeDL')
def test_get_video_metadata_download_error(mock_youtube_dl):
    mock_instance = mock_youtube_dl.return_value.__enter__.return_value
    mock_instance.extract_info.side_effect = yt_dlp.utils.DownloadError("Video not found", None)

    metadata = get_video_metadata("https://www.youtube.com/watch?v=nonexistent")
    assert "error" in metadata
    assert "Video not found" in metadata["error"]

def test_get_video_metadata_invalid_url():
    metadata = get_video_metadata("invalid-url")
    assert "error" in metadata
    assert "Invalid YouTube URL" in metadata["error"]

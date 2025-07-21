from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_metadata_valid_url():
    # This test requires a real YouTube URL and might be flaky
    # due to external network dependencies or YouTube changes.
    # For a more robust test, consider mocking the yt_dlp calls.
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Rick Astley - Never Gonna Give You Up
    response = client.get(f"/metadata?url={test_url}")
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "author" in data
    assert "thumbnail" in data
    assert "formats" in data
    assert data["title"] == "Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)"

def test_metadata_invalid_url():
    response = client.get("/metadata?url=invalid-url")
    assert response.status_code == 200 # The endpoint returns 200 even for errors
    assert response.json() == {"error": "Invalid YouTube URL"}

def test_download_audio():
    # This test is more complex as it involves streaming and temporary files.
    # For a real-world scenario, mocking yt-dlp would be essential.
    # Here, we'll just check if the endpoint returns a 200 OK status.
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    test_format_id = "140" # A common audio-only format for YouTube
    response = client.post(
        "/download",
        json={
            "url": test_url,
            "format_id": test_format_id
        }
    )
    assert response.status_code == 200
    assert response.headers['content-type'] == 'audio/mpeg'
    assert 'filename="Rick Astley - Never Gonna Give You Up' in response.headers['content-disposition']

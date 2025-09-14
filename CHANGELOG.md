# Changelog

All notable changes to this project will be documented in this file.

## 2025-09-14

### Added
- Backend progress tracking with in-memory store and new endpoint `GET /progress?task_id=<id>` (`main.py`).
- Frontend progress UI: polling `/progress` and showing stages in modal (`static/script.js`).
- Server-side progress callbacks in `utils/ytdlp_helper.py` (`downloading`, `download_complete`, `converting`, `streaming`, `completed`).

### Changed
- `Dockerfile`: `EXPOSE` updated from `8080` to `8000` to match default app port.
- `run.py`: `reload` controlled via `RELOAD` env var (default `false`).
- `README.md`: updated with progress info, clarified local run (FFmpeg requirement), corrected Docker port, documented `/progress`.

### Fixed
- Frontend format dropdown now correctly populated: backend adds `vcodec` in metadata, JS handles fallbacks (`ytdlp_helper.py`, `static/script.js`).
- Streaming stability: temp files now created in system temp dir; robust detection of yt-dlp output file with extension; improved cleanup logic (`utils/ytdlp_helper.py`).
- Clearer errors for missing dependencies: preflight checks for `yt-dlp` and `ffmpeg` with helpful messages (`main.py`).
- Accurate `media_type` selection based on file extension to improve browser handling (`main.py`).

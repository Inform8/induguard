@echo off
cd /d "%~dp0"
set PYTHONPATH=%~dp0
echo Starting InduGuard FastAPI Backend Server...
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
pause

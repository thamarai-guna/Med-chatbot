@echo off
set PYTHONIOENCODING=utf-8
set PYTHONPATH=.
call .venv\Scripts\activate.bat
python.exe -m uvicorn backend_api:app --reload --host 0.0.0.0 --port 8000

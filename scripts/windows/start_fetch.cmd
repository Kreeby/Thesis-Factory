@echo off
rem Restarts the full-text fetcher; .env must already be loaded into the environment (scripts\windows\load_env.ps1).
cd /d "%~dp0..\.."
"%CD%\venv\Scripts\python.exe" scripts\track.py --name "Full text fetch v2 (OpenAlex, free tier, Windows)" -- "%CD%\venv\Scripts\python.exe" scripts\fetch_fulltext.py --max-downloads 95 --days 6 >> .thesis-runs\logs\fetch.log 2>&1

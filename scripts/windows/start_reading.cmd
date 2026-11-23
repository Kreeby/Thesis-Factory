@echo off
rem Reads new fetched texts with qwen3; run ram_guard.ps1 alongside. Needs ollama serve with LLAMA_ARG_CACHE_RAM=0.
cd /d "%~dp0..\.."
"%CD%\venv\Scripts\python.exe" scripts\track.py --name "Deep reading (qwen3, Windows)" -- "%CD%\venv\Scripts\python.exe" scripts\read_papers.py --pause 5 >> .thesis-runs\logs\deep-reading-qwen3-windows.log 2>&1

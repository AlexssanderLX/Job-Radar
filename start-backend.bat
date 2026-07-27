@echo off
title Job Radar - Backend
cd /d "%~dp0backend"
echo Iniciando backend Job Radar em http://localhost:8000 ...
"C:\Users\Alexssander\anaconda3\python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause

@echo off
title Job Radar
echo Iniciando Job Radar...
start "Job Radar Backend" cmd /k "cd /d "%~dp0backend" && "C:\Users\Alexssander\anaconda3\python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8010"
timeout /t 3 /nobreak >nul
start "Job Radar Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"
timeout /t 5 /nobreak >nul
start "" "http://localhost:5174"
echo.
echo Backend: http://localhost:8010
echo Frontend: http://localhost:5174
echo Docs API: http://localhost:8010/docs
echo.
echo Feche as janelas do terminal para encerrar.

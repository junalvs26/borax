@echo off
echo ====================================================
echo   Iniciando Plataforma de IA Local BORAX (Engine C++)
echo ====================================================
echo.

echo [1/3] Iniciando Backend Python (FastAPI + C++ LLM + LanceDB)...
start "Backend BORAX" /min cmd /c "cd /d %~dp0backend && .\venv\Scripts\python.exe main.py"

echo [2/3] Iniciando Frontend React (Vite)...
start "Frontend BORAX" /min cmd /c "cd /d %~dp0frontend && npm run dev"

echo [3/3] Aguardando inicialização dos serviços...
ping -n 4 127.0.0.1 >nul

echo.
echo ====================================================
echo   Plataforma BORAX iniciada com sucesso!
echo   - Backend (C++ LLM): http://127.0.0.1:8000
echo   - Frontend:          http://localhost:1420
echo ====================================================
echo.
start http://localhost:1420

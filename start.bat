@echo off
title SLM local Server

if not exist "venv\Scripts\activate.bat" (
  echo [INFO] Ambiente virtuale non trovato. Creazione in corso...
  python -m venv venv
  call venv\Scripts\activate
  
  echo [INFO] Installazione delle dipendenze...
  pip install -r requirements.txt
) else (
  call venv\Scripts\activate
)

echo [INFO] Avvio dello script python...
python web_app.py

echo.
echo Il server si e' fermato o c'e' stato un errore
pause
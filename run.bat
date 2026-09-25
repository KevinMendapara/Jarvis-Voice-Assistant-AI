@echo off
cd /d "%~dp0"

:: If .venv doesn't exist, set it up from offline wheels (zero internet needed)
if not exist ".venv\Scripts\python.exe" (
    echo ========================================================
    echo  First time setup: Installing from offline wheels...
    echo  (No internet connection required)
    echo ========================================================
    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install --no-index --find-links=.\wheels -r requirements.txt
)

echo ========================================================
echo  Launching Jarvis Voice Assistant...
echo ========================================================
.\.venv\Scripts\python.exe jarvisUi.py
pause

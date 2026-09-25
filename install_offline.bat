@echo off
cd /d "%~dp0"
echo ========================================================
echo  Installing Jarvis dependencies OFFLINE (No Internet)
echo ========================================================
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --no-index --find-links=.\wheels -r requirements.txt
echo.
echo ========================================================
echo  [SUCCESS] All packages installed into .venv offline!
echo ========================================================
pause

@echo off
cd /d "%~dp0"
".venv\Scripts\python.exe" scripts\transfer_database.py
echo.
pause

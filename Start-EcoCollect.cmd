@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-EcoCollect.ps1"
if errorlevel 1 pause

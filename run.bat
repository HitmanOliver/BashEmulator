@echo off
chcp 65001 >nul
cd /d "%~dp0"
python src\EmuBash.py --config src\config.toml
if errorlevel 1 pause

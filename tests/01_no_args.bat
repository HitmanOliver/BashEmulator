@echo off
chcp 65001 >nul
cd /d "%~dp0.."

echo [TEST 01] Запуск без аргументов
echo Ожидается: vfs_root и startup_script из config.toml
echo.

python src\EmuBash.py

if errorlevel 1 pause

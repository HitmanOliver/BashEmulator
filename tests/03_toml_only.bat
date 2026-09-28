@echo off
chcp 65001 >nul
cd /d "%~dp0.."

echo [TEST 03] Только --config, остальное из TOML
echo Ожидается: vfs_root и startup_script взяты из config.toml
echo.

python src\EmuBash.py --config ./src/config.toml

if errorlevel 1 pause

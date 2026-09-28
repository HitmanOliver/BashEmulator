@echo off
chcp 65001 >nul
cd /d "%~dp0.."

echo [TEST 02] Только командная строка, без --config
echo Ожидается: vfs_root и startup_script взяты из CLI
echo.

python src\EmuBash.py ^
  --vfs-root ./vfs ^
  --startup-script ./src/startup.txt

if errorlevel 1 pause

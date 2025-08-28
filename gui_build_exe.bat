@echo off
setlocal
cd /d "%~dp0"

REM Local builds should not create or require version.txt.
REM The app will display 'not_released' at runtime via utils.get_version().

REM --- Clean old build --------------------------------------------------------
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

REM --- Install deps -----------------------------------------------------------
pip install -r requirements.txt
pip install pyinstaller

REM --- Build (spec tolerates missing version.txt) -----------------------------
pyinstaller --noconfirm gui_launcher.spec

if not exist "dist\as6-migration-tools.exe" (
  echo [ERROR] Expected output dist\as6-migration-tools.exe was not found.
  exit /b 1
)

REM --- Optional: rename to make local/dev builds obvious ----------------------
ren "dist\as6-migration-tools.exe" "as6-migration-tools-dev.exe" >nul 2>&1

echo.
if exist "dist\as6-migration-tools-dev.exe" (
  echo Done! Find it at: dist\as6-migration-tools-dev.exe
) else (
  echo Done! Find it at: dist\as6-migration-tools.exe
)
endlocal

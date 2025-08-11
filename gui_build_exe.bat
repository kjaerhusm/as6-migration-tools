@echo off
setlocal
cd /d "%~dp0"

REM --- Read version number ----------------------------------------------------
if not exist "version.txt" (
  echo [ERROR] version.txt not found.
  exit /b 1
)
set /p VERSION=< "version.txt"
if "%VERSION%"=="" (
  echo [ERROR] version.txt is empty or invalid.
  exit /b 1
)

echo Building as6-migration-tools-v%VERSION%.exe...

REM --- Create and activate a dedicated virtual environment --------------------
python -m venv .venv || (
  echo [ERROR] Failed to create virtual environment.
  exit /b 1
)
call .venv\Scripts\activate

REM --- Show interpreter used for the build (sanity check) ---------------------
python -c "import sys; print('Python:', sys.version); print('Executable:', sys.executable)" || (
  echo [ERROR] Python is not available inside the venv.
  exit /b 1
)

REM --- Install build requirements --------------------------------------------
python -m pip install --upgrade pip wheel setuptools || (
  echo [ERROR] Failed to upgrade pip/wheel/setuptools.
  exit /b 1
)
pip install -r requirements.txt || (
  echo [ERROR] Failed to install project requirements.
  exit /b 1
)
pip install pyinstaller || (
  echo [ERROR] Failed to install PyInstaller.
  exit /b 1
)

REM --- Preflight: verify critical modules are importable ----------------------
python -c "import CTkMessagebox; print('CTkMessagebox OK')" || (
  echo [ERROR] CTkMessagebox is not importable in this environment.
  exit /b 1
)

REM --- Build executable using the .spec file ----------------------------------
python -m PyInstaller --clean --noconfirm gui_launcher.spec
if errorlevel 1 (
  echo [ERROR] Build failed.
  exit /b 1
)

REM --- Cleanup intermediate build folder --------------------------------------
if exist "build" rmdir /s /q "build"

REM --- Prepare final artifact name -------------------------------------------
if exist "dist\as6-migration-tools-v%VERSION%.exe" del /f /q "dist\as6-migration-tools-v%VERSION%.exe"

if not exist "dist\as6-migration-tools.exe" (
  echo [ERROR] Expected output dist\as6-migration-tools.exe was not found.
  exit /b 1
)

ren "dist\as6-migration-tools.exe" "as6-migration-tools-v%VERSION%.exe" || (
  echo [ERROR] Failed to rename the executable.
  exit /b 1
)

echo Done! Find it at: dist\as6-migration-tools-v%VERSION%.exe
pause
endlocal

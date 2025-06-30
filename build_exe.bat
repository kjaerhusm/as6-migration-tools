@echo off
cd /d %~dp0

REM Read version number from version.txt
set /p VERSION=< version.txt

echo Building as6-migration-tools-v%VERSION%.exe...

REM Build EXE using PyInstaller
pyinstaller --clean --noconfirm gui_launcher.spec

IF ERRORLEVEL 1 (
    echo Build failed.
    pause
    exit /b 1
)

REM Remove build folder
rmdir /s /q build

REM Rename the output executable
ren dist\as6-migration-tools.exe as6-migration-tools-v%VERSION%.exe

echo Done! Find it at: dist\as6-migration-tools-v%VERSION%.exe
pause

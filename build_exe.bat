@echo off
echo Building BrdkMigrationTool.exe...
pyinstaller BrdkMigrationTool.spec
echo Done! Find your exe in /dist/BrdkMigrationTool/
pause

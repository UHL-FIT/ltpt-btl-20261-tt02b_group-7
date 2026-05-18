@echo off
echo ========================================================
echo DANG DON DEP CAC THU MUC VA FILE RAC...
echo ========================================================

if exist "build" rd /s /q "build"
if exist "dist" rd /s /q "dist"
if exist "SmartAttend.spec" del "SmartAttend.spec"
if exist "Setup_SmartAttend.exe" del "Setup_SmartAttend.exe"

echo Xoa cac thu muc __pycache__ va file .pyc...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc >nul 2>&1

echo Xoa file log...
if exist "data\app.log" del "data\app.log"

echo ========================================================
echo HOAN TAT DON DEP!
echo ========================================================
pause

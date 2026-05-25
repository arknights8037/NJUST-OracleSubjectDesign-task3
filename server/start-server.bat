@echo off
setlocal
cd /d "%~dp0" || exit /b 1

echo ================================================
echo   Backend Service
echo ================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [backend] creating virtual environment...
    python -m venv .venv
    if errorlevel 1 goto :fail
)

if not exist ".venv\Scripts\pip.exe" goto :fail

echo [backend] installing dependencies if needed...
.venv\Scripts\pip install -r requirements.txt
if errorlevel 1 goto :fail

echo [backend] starting FastAPI on http://localhost:8000 ...
.venv\Scripts\python run.py
if errorlevel 1 goto :fail

exit /b 0

:fail
echo.
echo [backend] failed to start. Check the messages above.
pause
exit /b 1

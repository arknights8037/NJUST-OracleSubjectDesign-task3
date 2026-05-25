@echo off
setlocal
title HRMS Launcher

set "ROOT=%~dp0"
cd /d "%ROOT%" || exit /b 1

echo ================================================
echo   HRMS One-Click Launcher
echo ================================================
echo.

echo [backend] output will appear in the new window: Backend Service
start "Backend Service" cmd /k call "%ROOT%server\start-server.bat"

timeout /t 3 /nobreak >nul

echo [frontend] output will appear in the new window: Frontend Service
start "Frontend Service" cmd /k call "%ROOT%client\start-client.bat"

echo.
echo ================================================
echo  Backend API : http://localhost:8000
echo  API Docs    : http://localhost:8000/docs
echo  Frontend UI : http://localhost:5173
echo  Default User: admin / admin123
echo ================================================
echo.
echo This window only launches child service windows.
echo Check Backend Service and Frontend Service for logs.
pause
exit /b 0

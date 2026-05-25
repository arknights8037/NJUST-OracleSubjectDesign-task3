@echo off
setlocal
cd /d "%~dp0" || exit /b 1

echo ================================================
echo   Frontend Service
echo ================================================
echo.

where pnpm >nul 2>&1
if errorlevel 1 goto :no_pnpm

if not exist "node_modules" (
    echo [frontend] installing dependencies with pnpm...
    call pnpm install --ignore-scripts=false
    if errorlevel 1 goto :fail
)

echo [frontend] checking vite runtime...
call pnpm exec vite --version >nul 2>&1
if errorlevel 1 (
    echo [frontend] vite bootstrap failed. Run pnpm approve-builds and retry.
    goto :fail
)

echo [frontend] starting Vite on http://localhost:5173 ...
call pnpm run dev
if errorlevel 1 goto :fail

exit /b 0

:no_pnpm
echo [frontend] pnpm not found. Run: npm install -g pnpm
pause
exit /b 1

:fail
echo.
echo [frontend] failed to start. Check the messages above.
pause
exit /b 1

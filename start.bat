@echo off
title Nekosui Launcher

cd /d "%~dp0"

echo.
echo ====================================
echo   Nekosui - Starting...
echo ====================================
echo.

if not exist "backend\requirements.txt" (
    echo [ERROR] Setup not complete. Run setup.bat first.
    pause
    exit /b 1
)

echo [1/3] Checking for updates...
for /f %%i in ('git rev-parse HEAD 2^>nul') do set LOCAL=%%i
for /f "tokens=1" %%i in ('git ls-remote origin HEAD 2^>nul') do set REMOTE=%%i

if defined LOCAL if defined REMOTE if not "%LOCAL%"=="%REMOTE%" (
    echo [!!] Update available!
    set /p UPDATE="    Update now? (y/N): "
    if /i "%UPDATE%"=="y" (
        echo     Updating...
        git pull --quiet
        cd frontend && npm install --prefer-offline --silent && cd ..
        cd backend && python -m pip install -r requirements.txt --quiet && cd ..
        echo [OK] Update complete.
    )
) else (
    echo [OK] Already up to date.
)

echo.
echo [2/3] Starting backend...
start "Nekosui Backend" cmd /k "cd /d "%~dp0backend" && python -m uvicorn main:app --reload --port 8000"

timeout /t 3 /nobreak > nul

echo [3/3] Starting frontend...
start "Nekosui Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

timeout /t 4 /nobreak > nul

start http://localhost:5173

echo.
echo ====================================
echo   Nekosui is running!
echo   http://localhost:5173
echo ====================================
echo.
pause

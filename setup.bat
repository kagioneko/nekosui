@echo off
title Nekosui Setup

cd /d "%~dp0"

echo.
echo ====================================
echo   Nekosui - First Time Setup
echo ====================================
echo.

REM 前提チェック
for %%c in (git python node npm) do (
    where %%c >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] %%c not found. Please install it first.
        echo.
        echo   Git    : https://git-scm.com/download/win
        echo   Python : https://www.python.org/downloads/
        echo   Node   : https://nodejs.org/
        echo.
        pause
        exit /b 1
    )
    echo [OK] %%c found.
)

REM neurostate-engine のクローン
echo.
echo Checking neurostate-engine...
if exist "..\neurostate-engine" (
    echo [OK] neurostate-engine already exists.
    cd ..\neurostate-engine && git pull --quiet && cd /d "%~dp0"
) else (
    echo Cloning neurostate-engine...
    git clone https://github.com/kagioneko/neurostate-engine ..\neurostate-engine
    echo [OK] neurostate-engine cloned.
)

REM バックエンド
echo.
echo Setting up backend...
if not exist "backend" mkdir backend
cd backend
python -m pip install -r requirements.txt --quiet
if not exist ".env" (
    copy .env.example .env
    echo [OK] .env created.
    echo.
    echo ----------------------------------------
    echo  API key is optional but recommended.
    echo  Edit backend\.env to add your key.
    echo  Supported: ANTHROPIC / OPENAI / GEMINI
    echo ----------------------------------------
) else (
    echo [OK] .env already exists.
)
cd /d "%~dp0"

REM フロントエンド
echo.
echo Setting up frontend...
if not exist "frontend" mkdir frontend
cd frontend
npm install
cd /d "%~dp0"

echo.
echo ====================================
echo   Setup complete!
echo   Run start.bat to launch.
echo ====================================
echo.
pause

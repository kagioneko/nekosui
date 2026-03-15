@echo off
chcp 65001 > nul
title ネコスイ ランチャー

echo.
echo ====================================
echo   ネコスイ 起動中...
echo ====================================
echo.

cd /d "%~dp0"

REM セットアップ確認
if not exist "backend\requirements.txt" (
    echo [!!] セットアップが完了していません。
    echo      setup.bat を先に実行してください。
    pause
    exit /b 1
)

REM アップデート確認
echo [1/3] アップデート確認中...
for /f %%i in ('git rev-parse HEAD 2^>nul') do set LOCAL=%%i
for /f %%i in ('git ls-remote origin HEAD 2^>nul') do set REMOTE=%%i
set REMOTE=%REMOTE%

if not "%LOCAL%"=="%REMOTE:~0,40%" (
    echo.
    echo [!!] 新しいバージョンがあります！
    set /p UPDATE="    アップデートしますか？ (y/N): "
    if /i "%UPDATE%"=="y" (
        echo     アップデート中...
        git pull --quiet
        cd frontend && npm install --prefer-offline --silent && cd ..
        cd backend && python -m pip install -r requirements.txt --quiet && cd ..
        echo [OK] アップデート完了
    )
) else (
    echo [OK] 最新バージョンです
)

REM バックエンド起動
echo.
echo [2/3] バックエンド起動中...
start "ネコスイ バックエンド" cmd /k "cd /d "%~dp0backend" && python -m uvicorn main:app --reload --port 8000"

REM 少し待つ
timeout /t 3 /nobreak > nul

REM フロントエンド起動
echo [3/3] フロントエンド起動中...
start "ネコスイ フロントエンド" cmd /k "cd /d "%~dp0frontend" && npm run dev"

REM ブラウザを開く
timeout /t 4 /nobreak > nul
start http://localhost:5173

echo.
echo ====================================
echo   起動完了！
echo ====================================
echo.
echo   ブラウザで http://localhost:5173 を開いてください
echo   終了するには各ウィンドウで Ctrl+C を押してください
echo.
pause

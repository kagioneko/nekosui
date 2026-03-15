# ネコスイ 起動スクリプト
# setup.ps1 を実行済みの場合、これをダブルクリックするだけで起動できます

$ErrorActionPreference = "Stop"
$Host.UI.RawUI.WindowTitle = "ネコスイ ランチャー"

function Write-Step($msg) {
    Write-Host ""
    Write-Host ">>> $msg" -ForegroundColor Cyan
}

function Write-OK($msg) {
    Write-Host "  [OK] $msg" -ForegroundColor Green
}

function Write-Warn($msg) {
    Write-Host "  [!!] $msg" -ForegroundColor Yellow
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host ""
Write-Host "====================================" -ForegroundColor Magenta
Write-Host "  ネコスイ 起動中..." -ForegroundColor Magenta
Write-Host "====================================" -ForegroundColor Magenta

# --- セットアップ確認 ---
$backendDir  = Join-Path $scriptDir "backend"
$frontendDir = Join-Path $scriptDir "frontend"

if (-not (Test-Path (Join-Path $backendDir "requirements.txt"))) {
    Write-Warn "セットアップが完了していません。setup.bat を先に実行してください。"
    Read-Host "Enterで閉じる"
    exit 1
}

# --- アップデート確認 ---
Write-Step "アップデート確認"

$localHash  = git rev-parse HEAD 2>$null
$remoteHash = git ls-remote origin HEAD 2>$null | ForEach-Object { ($_ -split "\s+")[0] }

if ($localHash -and $remoteHash -and ($localHash -ne $remoteHash)) {
    Write-Warn "新しいバージョンがあります！"
    $doUpdate = Read-Host "  今すぐアップデートしますか？(Y/n)"
    if ($doUpdate -ne "n" -and $doUpdate -ne "N") {
        Write-Host "  アップデート中..." -ForegroundColor White
        git pull --quiet
        Write-Host "  npm install 中..." -ForegroundColor White
        Set-Location $frontendDir
        npm install --prefer-offline 2>&1 | Out-Null
        Set-Location $scriptDir
        Write-Host "  pip install 中..." -ForegroundColor White
        Set-Location $backendDir
        python -m pip install -r requirements.txt --quiet
        Set-Location $scriptDir
        Write-OK "アップデート完了"
    } else {
        Write-Warn "アップデートをスキップしました"
    }
} else {
    Write-OK "最新バージョンです"
}

# --- neurostate-engine アップデート ---
$neuroDir = Join-Path (Split-Path -Parent $scriptDir) "neurostate-engine"
if (Test-Path $neuroDir) {
    Set-Location $neuroDir
    git pull --quiet 2>$null
    Set-Location $scriptDir
}

# --- バックエンド起動 ---
Write-Step "バックエンド起動"

# バックエンド起動コマンドをファイルに書き出して実行（引数エスケープ問題を回避）
$backendCmd = "Set-Location '$backendDir'; `$Host.UI.RawUI.WindowTitle = 'ネコスイ バックエンド'; python -m uvicorn main:app --reload --port 8000; Write-Host ''; Write-Host 'サーバーが停止しました' -ForegroundColor Red; Read-Host 'Enterで閉じる'"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

Write-OK "バックエンドを起動しました（ポート 8000）"

# バックエンドが立ち上がるまで少し待つ
Start-Sleep -Seconds 3

# --- フロントエンド起動 ---
Write-Step "フロントエンド起動"

$frontendCmd = "Set-Location '$frontendDir'; `$Host.UI.RawUI.WindowTitle = 'ネコスイ フロントエンド'; npm run dev; Write-Host ''; Write-Host 'サーバーが停止しました' -ForegroundColor Red; Read-Host 'Enterで閉じる'"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd -WindowStyle Normal

Write-OK "フロントエンドを起動しました（ポート 5173）"

# フロントエンドが立ち上がるまで少し待つ
Start-Sleep -Seconds 4

# --- ブラウザを開く ---
Write-Step "ブラウザを起動"
Start-Process "http://localhost:5173"
Write-OK "ブラウザを開きました"

Write-Host ""
Write-Host "====================================" -ForegroundColor Magenta
Write-Host "  ネコスイ 起動完了！" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "  ブラウザで http://localhost:5173 を開いてください" -ForegroundColor White
Write-Host "  終了するには各ターミナルウィンドウで Ctrl+C を押してください" -ForegroundColor White
Write-Host ""
Read-Host "このウィンドウは閉じてOKです。Enterで閉じる"

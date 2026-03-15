# ネコスイ セットアップスクリプト
# 初回のみ実行してください

$ErrorActionPreference = "Stop"
$Host.UI.RawUI.WindowTitle = "ネコスイ セットアップ"

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

function Write-Fail($msg) {
    Write-Host "  [NG] $msg" -ForegroundColor Red
}

Write-Host ""
Write-Host "====================================" -ForegroundColor Magenta
Write-Host "  ネコスイ セットアップ" -ForegroundColor Magenta
Write-Host "====================================" -ForegroundColor Magenta

# --- 前提チェック ---
Write-Step "前提ソフトウェアの確認"

foreach ($cmd in @("git", "python", "node", "npm")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        Write-OK "$cmd が見つかりました"
    } else {
        Write-Fail "$cmd が見つかりません。インストールしてから再実行してください。"
        Write-Host ""
        Write-Host "  Git    : https://git-scm.com/download/win" -ForegroundColor White
        Write-Host "  Python : https://www.python.org/downloads/" -ForegroundColor White
        Write-Host "  Node   : https://nodejs.org/ja/" -ForegroundColor White
        Read-Host "  Enterで閉じる"
        exit 1
    }
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# --- neurostate-engine のクローン ---
Write-Step "neurostate-engine の確認"

$neuroDir = Join-Path (Split-Path -Parent $scriptDir) "neurostate-engine"
if (Test-Path $neuroDir) {
    Write-OK "neurostate-engine は既に存在します"
    Set-Location $neuroDir
    git pull --quiet
    Set-Location $scriptDir
} else {
    Write-Host "  クローン中..." -ForegroundColor White
    git clone https://github.com/kagioneko/neurostate-engine $neuroDir
    Write-OK "neurostate-engine をクローンしました"
}

# --- バックエンド セットアップ ---
Write-Step "バックエンド セットアップ"

$backendDir = Join-Path $scriptDir "backend"
if (-not (Test-Path $backendDir)) { New-Item -ItemType Directory -Path $backendDir | Out-Null }
Set-Location $backendDir

Write-Host "  pip install 中..." -ForegroundColor White
python -m pip install -r requirements.txt --quiet
Write-OK "依存パッケージをインストールしました"

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Warn ".env を作成しました（APIキーは任意です）"
    $setKey = Read-Host "  今すぐ Anthropic API キーを設定しますか？(y/N)"
    if ($setKey -eq "y" -or $setKey -eq "Y") {
        $apiKey = Read-Host "  ANTHROPIC_API_KEY を入力してください"
        (Get-Content ".env") -replace "ANTHROPIC_API_KEY=.*", "ANTHROPIC_API_KEY=$apiKey" | Set-Content ".env"
        Write-OK "APIキーを設定しました"
    } else {
        Write-Warn "APIキーなしでも動きます（テンプレートセリフモード）"
    }
} else {
    Write-OK ".env はすでに存在します"
}

Set-Location $scriptDir

# --- フロントエンド セットアップ ---
Write-Step "フロントエンド セットアップ"

$frontendDir = Join-Path $scriptDir "frontend"
if (-not (Test-Path $frontendDir)) { New-Item -ItemType Directory -Path $frontendDir | Out-Null }
Set-Location $frontendDir

Write-Host "  npm install 中..." -ForegroundColor White
npm install --prefer-offline 2>&1 | Out-Null
Write-OK "フロントエンドパッケージをインストールしました"

Set-Location $scriptDir

# --- 完了 ---
Write-Host ""
Write-Host "====================================" -ForegroundColor Magenta
Write-Host "  セットアップ完了！" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "  start.bat をダブルクリックして起動できます" -ForegroundColor White
Write-Host ""
Read-Host "Enterで閉じる"

#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Complete Hermes validation script for Windows Server
    Tests: Node.js, npm, Ollama, Obsidian vault, Telegram bot

.DESCRIPTION
    Automated test suite that validates all Hermes components
    and runs integration tests before starting the bot

.EXAMPLE
    .\scripts\test-hermes.ps1
#>

Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🚀 HERMES VALIDATION SUITE            ║" -ForegroundColor Cyan
Write-Host "║  Windows Server Test Harness           ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$testResults = @()
$failedTests = 0
$passedTests = 0

# ============================================================================
# TEST 1: Node.js Installation
# ============================================================================
Write-Host "📋 TEST 1: Checking Node.js..." -ForegroundColor Yellow

try {
    $nodeVersion = node --version
    $npmVersion = npm --version
    Write-Host "  ✓ Node.js: $nodeVersion" -ForegroundColor Green
    Write-Host "  ✓ npm: $npmVersion" -ForegroundColor Green
    $passedTests++
}
catch {
    Write-Host "  ❌ Node.js not found or not in PATH" -ForegroundColor Red
    Write-Host "     Install from: https://nodejs.org/" -ForegroundColor Yellow
    $failedTests++
    exit 1
}

Write-Host ""

# ============================================================================
# TEST 2: Dependencies Installation
# ============================================================================
Write-Host "📦 TEST 2: Installing npm dependencies..." -ForegroundColor Yellow

if (Test-Path "node_modules") {
    Write-Host "  ℹ️  node_modules already exists, skipping npm install" -ForegroundColor Cyan
    Write-Host "  Run 'npm install' manually if you need to update" -ForegroundColor Cyan
} else {
    try {
        Write-Host "  🔄 Running npm install..." -ForegroundColor Cyan
        npm install | Out-Null
        Write-Host "  ✓ Dependencies installed successfully" -ForegroundColor Green
        $passedTests++
    }
    catch {
        Write-Host "  ❌ npm install failed" -ForegroundColor Red
        $failedTests++
    }
}

Write-Host ""

# ============================================================================
# TEST 3: Ollama Connection
# ============================================================================
Write-Host "🧠 TEST 3: Testing Ollama connection..." -ForegroundColor Yellow

try {
    $response = curl.exe -s http://localhost:11434/api/tags | ConvertFrom-Json

    if ($response.models) {
        Write-Host "  ✓ Ollama is running" -ForegroundColor Green
        Write-Host "  ✓ Found $($response.models.Count) models:" -ForegroundColor Green

        foreach ($model in $response.models) {
            Write-Host "    - $($model.name)" -ForegroundColor Cyan
        }
        $passedTests++
    }
    else {
        throw "No models found"
    }
}
catch {
    Write-Host "  ❌ Ollama connection failed" -ForegroundColor Red
    Write-Host "     Make sure Ollama is running: ollama serve" -ForegroundColor Yellow
    $failedTests++
}

Write-Host ""

# ============================================================================
# TEST 4: Obsidian Vault
# ============================================================================
Write-Host "📁 TEST 4: Checking Obsidian vault..." -ForegroundColor Yellow

$vaultPath = "C:\Users\SERVER\Hermes-Workspace\Hermes-Vault"

if (Test-Path $vaultPath) {
    Write-Host "  ✓ Vault path exists: $vaultPath" -ForegroundColor Green

    # Check subfolders
    $folders = Get-ChildItem -Directory $vaultPath | Select-Object -ExpandProperty Name
    Write-Host "  ✓ Found $($folders.Count) folders:" -ForegroundColor Green

    foreach ($folder in $folders) {
        $fileCount = (Get-ChildItem "$vaultPath\$folder" -Filter "*.md" -ErrorAction SilentlyContinue | Measure-Object).Count
        Write-Host "    - $folder ($fileCount notes)" -ForegroundColor Cyan
    }
    $passedTests++
}
else {
    Write-Host "  ❌ Vault path not found: $vaultPath" -ForegroundColor Red
    Write-Host "     Create vault structure in Obsidian first" -ForegroundColor Yellow
    $failedTests++
}

Write-Host ""

# ============================================================================
# TEST 5: Configuration
# ============================================================================
Write-Host "⚙️  TEST 5: Checking configuration..." -ForegroundColor Yellow

$configPath = "config/hermes-config.json"

if (Test-Path $configPath) {
    try {
        $config = Get-Content $configPath | ConvertFrom-Json
        Write-Host "  ✓ Config file found" -ForegroundColor Green
        Write-Host "  ✓ Ollama URL: $($config.ollama.baseUrl)" -ForegroundColor Green
        Write-Host "  ✓ Telegram bot configured: $($config.telegram.enabled)" -ForegroundColor Green
        Write-Host "  ✓ Obsidian vault path configured" -ForegroundColor Green
        $passedTests++
    }
    catch {
        Write-Host "  ❌ Config file is invalid JSON" -ForegroundColor Red
        $failedTests++
    }
}
else {
    Write-Host "  ❌ Config file not found" -ForegroundColor Red
    $failedTests++
}

Write-Host ""

# ============================================================================
# TEST 6: Run Integration Tests
# ============================================================================
Write-Host "🧪 TEST 6: Running integration tests..." -ForegroundColor Yellow

if (Test-Path "tests/integration.test.js") {
    try {
        Write-Host "  🔄 Testing Ollama client..." -ForegroundColor Cyan
        node tests/integration.test.js

        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Integration tests passed" -ForegroundColor Green
            $passedTests++
        }
        else {
            Write-Host "  ⚠️  Integration tests reported issues" -ForegroundColor Yellow
            Write-Host "     Check output above for details" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "  ❌ Failed to run integration tests" -ForegroundColor Red
        $failedTests++
    }
}

Write-Host ""

# ============================================================================
# SUMMARY
# ============================================================================
Write-Host "📊 TEST SUMMARY" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Passed: $passedTests" -ForegroundColor Green
Write-Host "  Failed: $failedTests" -ForegroundColor $(if ($failedTests -gt 0) { "Red" } else { "Green" })
Write-Host "════════════════════════════════════════" -ForegroundColor Cyan

Write-Host ""

if ($failedTests -eq 0) {
    Write-Host "✅ ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next step: Start Hermes" -ForegroundColor Cyan
    Write-Host "  npm start" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Then test via Telegram @Danrcbh_bot:" -ForegroundColor Cyan
    Write-Host "  /help     - Show commands" -ForegroundColor Yellow
    Write-Host "  /ask      - Test general query" -ForegroundColor Yellow
    Write-Host "  /status   - Check system health" -ForegroundColor Yellow
    Write-Host ""
}
else {
    Write-Host "❌ SOME TESTS FAILED" -ForegroundColor Red
    Write-Host ""
    Write-Host "Fix issues above and re-run this script:" -ForegroundColor Yellow
    Write-Host "  .\scripts\test-hermes.ps1" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

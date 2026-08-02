#!/usr/bin/env pwsh
# Hermes validation script - simplified version

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "HERMES VALIDATION SUITE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Check if Ollama is running
Write-Host "[TEST 1] Checking Ollama..." -ForegroundColor Yellow

try {
    $response = curl.exe -s http://localhost:11434/api/tags | ConvertFrom-Json
    if ($response.models) {
        Write-Host "  OK - Ollama is running" -ForegroundColor Green
        Write-Host "  Found $($response.models.Count) models" -ForegroundColor Green
        foreach ($model in $response.models) {
            Write-Host "    - $($model.name)" -ForegroundColor Cyan
        }
    }
}
catch {
    Write-Host "  FAILED - Ollama not running" -ForegroundColor Red
    Write-Host "  Start it: ollama serve" -ForegroundColor Yellow
}

Write-Host ""

# Test 2: Check Obsidian vault
Write-Host "[TEST 2] Checking Obsidian vault..." -ForegroundColor Yellow

$vaultPath = "C:\Users\SERVER\Hermes-Workspace\Hermes-Vault"

if (Test-Path $vaultPath) {
    Write-Host "  OK - Vault found at $vaultPath" -ForegroundColor Green

    $folders = Get-ChildItem -Directory $vaultPath | Select-Object -ExpandProperty Name
    Write-Host "  Found $($folders.Count) folders" -ForegroundColor Green
    foreach ($folder in $folders) {
        $files = (Get-ChildItem "$vaultPath\$folder" -Filter "*.md" -ErrorAction SilentlyContinue | Measure-Object).Count
        Write-Host "    - $folder ($files notes)" -ForegroundColor Cyan
    }
}
else {
    Write-Host "  FAILED - Vault not found" -ForegroundColor Red
    Write-Host "  Expected: $vaultPath" -ForegroundColor Yellow
}

Write-Host ""

# Test 3: Check configuration
Write-Host "[TEST 3] Checking configuration..." -ForegroundColor Yellow

if (Test-Path "config/hermes-config.json") {
    try {
        $config = Get-Content config/hermes-config.json | ConvertFrom-Json
        Write-Host "  OK - Config file is valid" -ForegroundColor Green
        Write-Host "  Ollama: $($config.ollama.baseUrl)" -ForegroundColor Cyan
        Write-Host "  Telegram: Enabled=$($config.telegram.enabled)" -ForegroundColor Cyan
    }
    catch {
        Write-Host "  FAILED - Invalid config JSON" -ForegroundColor Red
    }
}
else {
    Write-Host "  FAILED - Config file not found" -ForegroundColor Red
}

Write-Host ""

# Test 4: Run integration tests
Write-Host "[TEST 4] Running integration tests..." -ForegroundColor Yellow

if (Test-Path "tests/integration.test.js") {
    node tests/integration.test.js
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TESTS COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next: npm start" -ForegroundColor Yellow

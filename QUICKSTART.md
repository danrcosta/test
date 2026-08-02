# 🚀 Hermes Quick Start

Get Hermes running in 3 minutes.

## Prerequisites

- ✓ Windows Server
- ✓ Node.js 18+ installed
- ✓ Ollama running (`ollama serve`)
- ✓ Obsidian vault at `C:\Users\SERVER\Hermes-Workspace\Hermes-Vault`

## Step 1: Navigate to Repo

```powershell
cd path/to/hermes-obsidian
```

## Step 2: Run Validation Tests

Execute the automated test suite:

```powershell
.\scripts\test-hermes.ps1
```

This will:
- ✓ Check Node.js installation
- ✓ Install npm dependencies
- ✓ Test Ollama connection
- ✓ Verify Obsidian vault
- ✓ Validate configuration
- ✓ Run integration tests

**Expected output:**
```
✅ ALL TESTS PASSED!

Next step: Start Hermes
  npm start
```

## Step 3: Start Hermes

```powershell
npm start
```

**Expected output:**
```
╔════════════════════════════════════════╗
║  🚀 HERMES - Central Orchestration Hub║
║  Powered by Nous Agent + Ollama         ║
╚════════════════════════════════════════╝

✓ Ollama connected
✓ Obsidian vault connected
✓ Telegram bot connected

💬 Telegram bot listening for commands...
```

## Step 4: Test via Telegram

Open Telegram and message **@Danrcbh_bot**:

```
/help              → Show all commands
/ask What is AI?   → Test general query
/think [question]  → Test deep reasoning
/code [request]    → Test code generation
/note [text]       → Save to inbox
/status            → Check system status
```

## Troubleshooting

### Tests fail with "Ollama connection refused"
```powershell
# Start Ollama
ollama serve
```

### Tests fail with "Vault path not found"
```powershell
# Verify vault exists
Test-Path "C:\Users\SERVER\Hermes-Workspace\Hermes-Vault"

# Create if missing (in Obsidian GUI first)
```

### npm install fails
```powershell
# Clear cache and retry
npm cache clean --force
npm install
```

### Telegram bot not responding
- Verify bot token in `config/hermes-config.json`
- Check internet connection
- Restart with `npm start`

## Development Mode (Auto-Reload)

```powershell
npm run dev
```

Bot will restart automatically when you edit files.

## Next Steps

1. ✅ Run validation tests
2. ✅ Start bot
3. ✅ Test Telegram commands
4. → **Setup vault sync** (auto-commit to git)
5. → **Enable MCP logging** (Slack/Notion)
6. → **Add Python support** (optional)

---

**Status**: Ready to test  
**Time**: ~5 minutes to full operation  
**Support**: See `docs/WINDOWS-SETUP.md` for detailed guide

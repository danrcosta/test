# Hermes Setup for Windows Server

Complete guide to running Hermes on your Windows Server with Ollama and Obsidian vault.

## Prerequisites Verification

### 1. Check Node.js
```powershell
# PowerShell on Windows Server
node --version    # Should be v18+ 
npm --version     # Should be v9+
```

If not installed, download from https://nodejs.org/

### 2. Verify Ollama is Running
```powershell
# Check if Ollama process is active
Get-Process ollama

# Or start it if needed
ollama serve
```

### 3. Verify Ollama Connection
```powershell
# Test Ollama endpoint
curl http://localhost:11434/api/tags

# Should return list of available models
```

## Installation Steps

### Step 1: Clone/Navigate to Repository
```powershell
cd C:\path\to\hermes-obsidian
```

### Step 2: Install Dependencies
```powershell
npm install
```

Expected output:
```
added 45 packages in 2.3s
```

### Step 3: Configure Paths

Edit `config/hermes-config.json`:
```json
{
  "obsidian": {
    "vaultPath": "C:\\Users\\SERVER\\Hermes-Workspace\\Hermes-Vault"
  },
  "ollama": {
    "baseUrl": "http://localhost:11434"
  }
}
```

### Step 4: Create .env File (optional)
```powershell
# Copy template
Copy-Item .env.example .env

# Edit with your settings
notepad .env
```

## Running Hermes

### Start the Bot
```powershell
npm start
```

Expected output:
```
╔════════════════════════════════════════╗
║  🚀 HERMES - Central Orchestration Hub║
║  Powered by Nous Agent + Ollama         ║
╚════════════════════════════════════════╝

✓ Ollama connected
✓ Obsidian vault connected
✓ Telegram bot connected

💬 Telegram bot listening for commands...
📁 Connected to Obsidian vault
🧠 Local Ollama models ready

Press Ctrl+C to stop
```

## Testing Locally

### 1. Run Integration Tests
```powershell
# Test Ollama + Obsidian connectivity
node tests/integration.test.js

# Expected:
# Testing Ollama connection...
#   Status: ✓ OK
#   Models found: 5
# Testing Obsidian vault...
#   Vault exists: ✓ Yes
```

### 2. Test MCP Integration
```powershell
# Test MCP services (Slack, Notion, Google Drive)
node tests/mcp-test.js

# Expected:
# 🧪 Testing MCP Integration...
# Testing Slack...
#   Result: ✓ OK
# Testing Notion...
#   Result: ✓ OK
```

### 3. Manually Test Hermes via Telegram

Once running, open Telegram and find **@Danrcbh_bot**:

```
/help              → Show available commands
/ask What is AI?   → General query
/think [question]  → Deep reasoning
/code [request]    → Code generation
/note [text]       → Save to inbox
/status            → System status
```

## Development Mode with Auto-Reload

```powershell
# Watch for changes and auto-reload
npm run dev
```

This uses nodemon for automatic restarts when you edit files.

## Troubleshooting

### "Cannot find module" error
```powershell
# Reinstall dependencies
rm node_modules -Recurse
npm install
```

### Ollama connection refused
```powershell
# Check if Ollama is running
Get-Process ollama

# Start Ollama if needed
ollama serve

# Or access it:
ollama list
```

### Obsidian vault not found
```powershell
# Verify path exists
Test-Path "C:\Users\SERVER\Hermes-Workspace\Hermes-Vault"

# List contents
Get-ChildItem "C:\Users\SERVER\Hermes-Workspace\Hermes-Vault"
```

### Telegram bot not responding
```powershell
# Check token is correct in config
# Verify internet connection
# Check firewall allows outbound HTTPS
```

## File Structure on Windows

```
C:\
└── Users\
    └── SERVER\
        └── Hermes-Workspace\
            ├── Hermes-Vault\        (Obsidian vault)
            │   ├── 00-inbox\
            │   ├── 01-daily\
            │   ├── 02-projects\
            │   └── ...
            └── hermes-obsidian\     (Code repository)
                ├── src\
                ├── config\
                ├── tests\
                └── package.json
```

## Performance Tips

### Optimize for Windows Server
1. **CPU Priority**
   ```powershell
   # Run Ollama on dedicated core (if multi-core available)
   Start-Process ollama -WindowStyle Minimized
   ```

2. **Memory Management**
   - Use smaller models during testing (qwen2.7b)
   - Monitor memory: `Get-WmiObject win32_operatingsystem | Select TotalVisibleMemorySize,FreePhysicalMemory`

3. **Disk Performance**
   - Keep Obsidian vault on fast disk (SSD preferred)
   - Monitor disk: `Get-Volume`

## Backup Vault Locally

```powershell
# Create daily backup
$date = Get-Date -Format "yyyy-MM-dd"
Copy-Item -Path "C:\Users\SERVER\Hermes-Workspace\Hermes-Vault" `
          -Destination "C:\Backups\Hermes-Vault-$date" -Recurse

# Later: Sync to Google Drive via MCP
```

## Network/Tailscale Setup (Optional)

To access Hermes remotely via Tailscale:

```powershell
# Check Tailscale IP
tailscale ip

# Should see: 100.xxx.x.x (your Tailscale IP)

# Access from other device:
# http://100.86.232.77:8080 (if webhook server running)
```

For now, Telegram bot works globally via polling (no network setup needed).

## Logs and Debugging

### View Hermes Logs
```powershell
# Logs appear in console during `npm start`
# To save to file, redirect output:
npm start > hermes.log 2>&1

# View log
Get-Content hermes.log -Tail 50
```

### Enable Debug Mode
```powershell
# Set environment variable
$env:DEBUG = "hermes:*"

# Then start
npm start
```

## Next Steps

1. ✅ Install and verify all components
2. ✅ Run tests locally
3. ✅ Test Telegram bot commands
4. [ ] Set up MCP logging (Notion)
5. [ ] Enable Google Drive backups
6. [ ] Configure git auto-commits
7. [ ] Add second bot for Claude requests

## Resources

- Ollama: https://ollama.ai
- Obsidian: https://obsidian.md
- Telegram Bot API: https://core.telegram.org/bots
- Node.js: https://nodejs.org

## Support

For issues:
1. Check troubleshooting section above
2. Review logs in console
3. Verify config in `config/hermes-config.json`
4. Check Obsidian vault structure

---

**Platform**: Windows Server  
**Node Version**: 18+  
**Status**: Ready for Testing  
**Last Updated**: 2026-08-02

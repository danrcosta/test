# Hermes Setup Guide

## Prerequisites

1. **Node.js** 18+ installed
2. **Ollama** running on Windows Server
3. **Obsidian** vault at `C:\Users\SERVER\Hermes-Workspace\Hermes-Vault`
4. **Telegram Bot Token** (@Danrcbh_bot)

## Installation

```bash
# Clone/navigate to repo
cd hermes-obsidian

# Install dependencies
npm install

# Copy env config
cp .env.example .env
```

## Configuration

### 1. Update `config/hermes-config.json`

Make sure paths are correct:
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

### 2. Verify Ollama

```bash
# Test Ollama connection
curl http://localhost:11434/api/tags

# Should return your available models:
# - deepseek-r1:14b-32k
# - qwen2.5-coder:14b-64k
# - mistral-nemo:12b-128k
# - qwen2.7b-128k
# - nomic-embed-text:latest
```

### 3. Check Obsidian Vault

```bash
# Verify vault structure exists
dir "C:\Users\SERVER\Hermes-Workspace\Hermes-Vault"

# Should have folders:
# 00-inbox, 01-daily, 02-projects, 03-people, 04-knowledge,
# 05-hermes, 06-financial, 07-health, 08-templates, 09-attachments,
# config, scripts
```

## Usage

### Start Hermes

```bash
npm start

# Or with auto-reload (development)
npm run dev
```

### Telegram Commands

Once running, message @Danrcbh_bot on Telegram:

- **/ask [question]** - General query using mistral-nemo
  ```
  /ask What is machine learning?
  ```

- **/think [question]** - Deep reasoning using deepseek-r1
  ```
  /think How should I approach learning AI?
  ```

- **/code [request]** - Generate code using qwen2.5-coder
  ```
  /code Create a Node.js HTTP server
  ```

- **/note [content]** - Save to Obsidian inbox
  ```
  /note Remember to update project documentation
  ```

- **/search [query]** - Search Obsidian vault (coming soon)
  ```
  /search productivity tips
  ```

- **/status** - Check system health
  ```
  /status
  ```

- **/help** - Show help
  ```
  /help
  ```

## Workflow

### Typical Use Case

1. **User sends Telegram message** → Bot receives via polling
2. **Process with Ollama** → Selected model processes request
3. **Save to Obsidian** → Results automatically saved to vault
4. **Response via Telegram** → User gets answer immediately

### Example: Deep Learning Question

```
User: /think What are the best practices for training neural networks?

↓ Hermes receives via Telegram

↓ Routes to deepseek-r1:14b-32k model

↓ Ollama generates detailed response (takes 30-60s)

↓ Auto-saves to 04-knowledge folder

↓ Sends response back to Telegram

User sees comprehensive answer + it's now in Second Brain
```

## Project Structure

```
hermes-obsidian/
├── config/
│   └── hermes-config.json       # Central config
├── src/
│   ├── index.js                 # Entry point
│   ├── hermes.js               # Main orchestrator
│   ├── ollama-client.js         # Ollama integration
│   ├── obsidian-client.js       # Obsidian integration
│   └── telegram-client.js       # Telegram integration
├── docs/
│   ├── SETUP.md                 # This file
│   └── ARCHITECTURE.md
├── package.json
├── .env.example
└── README.md
```

## Troubleshooting

### Ollama Connection Failed
```bash
# Check if Ollama is running
# PowerShell on Windows Server:
Get-Process ollama

# If not running, start it:
ollama serve
```

### Obsidian Vault Not Found
- Verify path: `C:\Users\SERVER\Hermes-Workspace\Hermes-Vault`
- Check permissions (should be readable/writable)
- Create missing folders if needed

### Telegram Bot Not Responding
- Verify token in `config/hermes-config.json`
- Check internet connection on Windows Server
- Restart bot: stop and run `npm start` again

### Model Not Found
```bash
# List available models
ollama list

# If model missing, pull it:
ollama pull deepseek-r1:14b-32k
ollama pull qwen2.5-coder:14b-64k
```

## Performance Tips

- **Fast responses**: Use `qwen2.7b-128k` (4.4 GB)
- **Balanced**: Use `mistral-nemo:12b-128k` (7.1 GB)
- **High quality**: Use `qwen2.5-coder` or `deepseek-r1` (9-11 GB)
- **Embeddings**: Always use `nomic-embed-text` for semantic search

## Next Steps

- [ ] Test basic commands
- [ ] Verify Obsidian integration
- [ ] Set up Claude bot for advanced requests
- [ ] Configure git auto-commit
- [ ] Add Tailscale remote access
- [ ] Create custom shortcuts in Telegram

## Remote Access

To access from other devices via Tailscale:

```
Server IP: 100.86.232.77
Port: 8080
```

The bot is accessible globally through Telegram, no VPN needed for that.

---

**Last Updated**: 2026-08-02  
**Status**: Initial Setup

# Hermes - Central AI Orchestration Hub

A unified AI productivity system integrating:
- **Nous Hermes Agent** - main orchestration
- **Obsidian** - Second Brain knowledge repository  
- **Ollama** - local LLM models (optimized tokens)
- **Telegram** - communication interface
- **Claude** - advanced reasoning capabilities

## Architecture

```
┌─────────────────────────────────────────┐
│      Telegram Interface (Input/Output)  │
│  • Hermes Bot (orchestration)           │
│  • Claude Bot (advanced requests)       │
└──────────────┬──────────────────────────┘
               │
        ┌──────▼──────┐
        │   HERMES    │ (Nous Agent - Hub)
        │   Central   │
        └──────┬──────┘
               │
      ┌────────┼────────┐
      ▼        ▼        ▼
   OLLAMA  OBSIDIAN  CLAUDE API
   (Local  (Second   (Advanced
   Models) Brain)    Reasoning)
```

## Quick Start

1. **Install dependencies**: `npm install`
2. **Configure**: Edit `config/hermes-config.json`
3. **Start services**: `npm start`

## Directory Structure

```
hermes-obsidian/
├── config/              # Central configuration
│   └── hermes-config.json
├── scripts/             # Integration scripts
│   ├── obsidian-sync.js
│   ├── telegram-webhook.js
│   └── ollama-client.js
├── src/                 # Source code
│   ├── hermes/         # Hermes integration
│   ├── obsidian/       # Obsidian API
│   └── utils/
├── docs/               # Documentation
│   ├── ARCHITECTURE.md
│   └── SETUP.md
└── package.json
```

## Key Features

- [x] Local Ollama integration (deepseek-r1, qwen2.5-coder, mistral-nemo)
- [ ] Obsidian vault sync
- [ ] Telegram webhook receiver
- [ ] Claude integration for advanced tasks
- [ ] Auto-git commit of important changes
- [ ] Tailscale remote access

## Models Available

| Model | Purpose | Size |
|-------|---------|------|
| deepseek-r1:14b-32k | Complex reasoning | 11 GB |
| qwen2.5-coder:14b-64k | Code generation | 9.0 GB |
| mistral-nemo:12b-128k | General purpose | 7.1 GB |
| qwen2.7b-128k | Fast responses | 4.4 GB |
| nomic-embed-text | Semantic search | 274 MB |

## Configuration

See `config/hermes-config.json` for:
- Ollama model selection
- Obsidian vault path
- Telegram bot tokens
- Network/Tailscale settings

## Usage

### From Telegram
```
/ask "Question for Hermes"
/claude "Need advanced reasoning"
/search "Search Obsidian"
/note "Save to inbox"
```

### Programmatic
```javascript
const hermes = require('./src/hermes');
const response = await hermes.query('Your question', { model: 'reasoning' });
```

## Development

- Branch: `claude/hermes-obsidian-pb4b1t`
- Commits automatically tracked to `05-hermes` in Obsidian

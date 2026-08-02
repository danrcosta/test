# Hermes Architecture

## System Overview

Hermes is a distributed AI orchestration system with three main layers:

```
┌─────────────────────────────────────────────────────┐
│              INPUT LAYER - Telegram                 │
│         @Danrcbh_bot (Polling / Webhooks)           │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│         ORCHESTRATION LAYER - Hermes                │
│  • Command routing & processing                     │
│  • Model selection & optimization                   │
│  • Obsidian integration                             │
│  • Context management                               │
└──────────────────┬──────────────────────────────────┘
                   │
     ┌─────────────┼─────────────┐
     │             │             │
┌────▼───┐  ┌──────▼─────┐  ┌───▼────────┐
│ OLLAMA  │  │  OBSIDIAN  │  │   CLAUDE   │
│(Local)  │  │(Local FS)  │  │  (Remote)  │
└────────┘  └────────────┘  └────────────┘
```

## Components

### 1. Telegram Layer (`telegram-client.js`)

**Purpose**: User interface and command input

**Features**:
- Polling mode for reliability
- Command parsing (`/ask`, `/think`, `/code`, `/note`, `/search`, `/status`)
- Response formatting (Markdown, HTML)
- Message editing and deletion

**Commands**:
```
/ask [text]      → General query
/think [text]    → Deep reasoning
/code [text]     → Code generation
/note [text]     → Save to inbox
/search [query]  → Search vault
/status          → System health
/help            → Show commands
```

### 2. Hermes Orchestration (`hermes.js`)

**Purpose**: Central decision engine and coordinator

**Responsibilities**:
- Initialize all subsystems
- Route commands to appropriate models
- Manage conversation context
- Handle errors and fallbacks
- Save interactions to Obsidian

**Command Routing Logic**:
```javascript
/ask → mistral-nemo:12b-128k (balanced, fast)
/think → deepseek-r1:14b-32k (reasoning, slower)
/code → qwen2.5-coder:14b-64k (specialized)
/note → Direct to Obsidian
```

### 3. Ollama Layer (`ollama-client.js`)

**Purpose**: Local LLM inference

**Models**:
| Model | Size | Use Case |
|-------|------|----------|
| deepseek-r1:14b-32k | 11 GB | Complex reasoning |
| qwen2.5-coder:14b-64k | 9.0 GB | Code generation |
| mistral-nemo:12b-128k | 7.1 GB | General purpose |
| qwen2.7b-128k | 4.4 GB | Fast responses |
| nomic-embed-text | 274 MB | Semantic search |

**API Endpoints**:
- `POST /api/generate` - Text generation
- `POST /api/embeddings` - Embedding vectors
- `GET /api/tags` - List models

### 4. Obsidian Layer (`obsidian-client.js`)

**Purpose**: Knowledge repository and Second Brain

**Vault Structure**:
```
Hermes-Vault/
├── 00-inbox/          # Quick captures
├── 01-daily/          # Daily notes
├── 02-projects/       # Project logs
├── 03-people/         # Contacts & relationships
├── 04-knowledge/      # Deep learning & insights
├── 05-hermes/         # Hermes system logs
├── 06-financial/      # Financial tracking
├── 07-health/         # Health & wellness
├── 08-templates/      # Note templates
├── 09-attachments/    # Files & media
├── config/            # Settings
└── scripts/           # Automation scripts
```

**Storage Strategy**:
- **Inbox**: Immediate captures (timestamp-based)
- **Daily**: Date-organized notes (YYYY-MM-DD)
- **Knowledge**: Structured learning (tagged)
- **Hermes**: System logs & queries

### 5. Claude Integration (Planned)

**Purpose**: Advanced reasoning for complex tasks

**When to Use**:
- Multi-step reasoning required
- Requires external knowledge
- Cost-benefit is acceptable
- User explicitly requests advanced analysis

**Mode**: Optional second Telegram bot (`@Claude_bot` or similar)

## Data Flow

### Example: User asks a question

```
1. User sends Telegram message
   ↓
2. TelegramClient receives via polling
   ↓
3. Message routed to Hermes.handleAsk()
   ↓
4. Hermes selects model: mistral-nemo
   ↓
5. OllamaClient.query(mistral-nemo, prompt)
   ↓
6. Ollama processes locally, returns response
   ↓
7. ObsidianClient.saveToDailyNote()
   ↓
8. TelegramClient sends formatted response back
   ↓
9. User receives answer + it's saved to vault
```

### Example: Save note to Obsidian

```
1. User: /note "Remember to read about transformers"
   ↓
2. TelegramClient parses command
   ↓
3. Hermes.handleNote()
   ↓
4. ObsidianClient.saveToInbox(title, content, tags)
   ↓
5. Creates file in 00-inbox/
   ↓
6. Returns filename to user
   ↓
7. User confirms save via Telegram
```

## Key Design Decisions

### 1. **Local-First Architecture**
- Ollama runs locally for low latency
- Obsidian vault is local file system
- Minimal external dependencies
- Better privacy and cost efficiency

### 2. **Fallback Strategy**
- If Ollama down → offer to use Claude
- If vault unreachable → buffer in memory
- If Telegram fails → retry with exponential backoff

### 3. **Token Optimization**
- Use fast models (`qwen2.7b`) for simple queries
- Reserve large models for complex tasks
- Use embeddings for semantic search
- Archive old notes to reduce context

### 4. **Polling vs Webhooks**
- Current: Telegram polling (more reliable, no firewall issues)
- Future: Webhooks on Tailscale VPN for instant response

## Scalability Considerations

### Current Load
- Single Windows Server
- Up to 10 concurrent Telegram users
- 5-30 second response times depending on model

### Future Scaling
- Add more Ollama instances on different servers
- Implement load balancing
- Cache common queries
- Implement vector database for semantic search

## Security

### Current Implementation
- Bot token stored in config (should move to env vars)
- Local vault access (no authentication needed locally)
- Telegram polling (no exposed endpoints)

### Recommendations
- Use `.env` file for sensitive data
- Implement user auth for vault access
- Rate limiting on bot commands
- Query logging and audit trail

## Performance Metrics

### Target Response Times
| Command | Model | Time |
|---------|-------|------|
| /ask | mistral-nemo | 5-15s |
| /think | deepseek-r1 | 30-120s |
| /code | qwen2.5-coder | 10-30s |
| /note | Direct save | <1s |
| /status | System check | <2s |

### Resource Usage
- RAM: ~24-32 GB (all models loaded)
- CPU: ~80% during inference
- Disk: ~45 GB (all models)
- Network: 100-500 KB/s (Telegram polling)

## Future Enhancements

### Phase 2
- [ ] Vector database (Weaviate/Milvus) for semantic search
- [ ] Claude bot integration for advanced reasoning
- [ ] Custom prompt templates
- [ ] Rate limiting and quotas

### Phase 3
- [ ] Web dashboard for monitoring
- [ ] Export/backup automation
- [ ] Multi-user support with permissions
- [ ] RAG (Retrieval Augmented Generation)

### Phase 4
- [ ] Mobile app
- [ ] Voice commands
- [ ] Real-time collaboration
- [ ] Advanced analytics

---

**Document Version**: 1.0  
**Last Updated**: 2026-08-02  
**Status**: Architecture Complete, Implementation In Progress

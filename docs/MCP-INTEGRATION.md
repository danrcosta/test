# MCP Integration Guide for Hermes

## Overview

Hermes can integrate with available MCP (Model Context Protocol) services for:
- **Distributed logging** → Notion
- **Real-time notifications** → Slack
- **Backup & archival** → Google Drive

## Available MCP Services

| Service | Status | Use Case |
|---------|--------|----------|
| **Slack** | ✓ Connected | Notifications, alerts |
| **Notion** | ✓ Connected | Query logging, knowledge base |
| **Google Drive** | ✓ Connected | Backup, file storage |
| **Gmail** | ✓ Connected | (Future: Email digest) |

## Architecture

```
Hermes Local
    ↓
┌───────────────────┐
│ MCP Integration   │
└───────────────────┘
    ↓ ↓ ↓
Slack Notion GDrive
```

## Setup

### 1. Enable MCP Services in Config

```json
{
  "mcp": {
    "enabled": true,
    "services": {
      "slack": {
        "enabled": true,
        "channels": [
          "#hermes-logs",
          "#hermes-alerts"
        ]
      },
      "notion": {
        "enabled": true,
        "database": "Hermes-Queries",
        "vault_backup": "Hermes-Vault-Sync"
      },
      "googleDrive": {
        "enabled": true,
        "folder": "Hermes",
        "backupInterval": 3600000
      }
    }
  }
}
```

### 2. Initialize in Hermes

```javascript
import MCPIntegration from './src/mcp-integration.js';

const mcp = new MCPIntegration(config.mcp);
await mcp.initialize();
```

## Usage Examples

### Log a Query

```javascript
await mcp.logQuery(
  'What is neural networks?',  // query
  'Neural networks are...',     // response
  'deepseek-r1',               // model
  2500                         // duration (ms)
);
// Auto-logs to Notion + Google Drive
```

### Send Alert to Slack

```javascript
await mcp.notifySlack(
  '#hermes-alerts',
  '⚠️ High memory usage: 85%'
);
```

### Backup Obsidian Vault

```javascript
const notes = await obsidian.listFiles('knowledge');
await mcp.backupToGoogleDrive(notes);
```

## Data Flow

### Query Execution with MCP Logging

```
1. User sends query via Telegram
   ↓
2. Hermes routes to Ollama
   ↓
3. Model generates response
   ↓
4. MCP Integration logs:
   - Notion: Save query + response
   - Google Drive: Archive conversation
   - Slack: Notify if > 60s processing
   ↓
5. Response sent to user + saved to Obsidian
```

### Daily Backup Cycle

```
Every 1 hour:
  ├─ Export Obsidian vault
  ├─ Upload to Google Drive (Hermes/Backups/)
  ├─ Log to Notion (Backup Database)
  └─ Notify Slack (#hermes-logs)
```

## Notion Databases

### Hermes-Queries
Logs all queries and responses for analysis.

**Properties:**
- Title: Query text
- Response: AI response (truncated)
- Model: Which Ollama model was used
- Duration: Processing time
- Timestamp: When query was made
- Tags: Categories (reasoning, coding, general)

### Hermes-Vault-Sync
Tracks Obsidian vault synchronization history.

**Properties:**
- Title: Sync event
- Status: Success/Failed
- Notes Count: Total notes synced
- Size: Vault size in MB
- Timestamp: When sync occurred

## Slack Channels

### #hermes-logs
General activity log:
```
✓ Query processed (mistral-nemo, 1.2s)
✓ 45 notes synced to vault
✓ Backup completed (2.3 MB)
```

### #hermes-alerts
Issues and warnings:
```
⚠️ Ollama response slow (5s+)
❌ Obsidian vault sync failed
🔄 Retrying failed sync...
```

## Google Drive Structure

```
Hermes/
├── Backups/
│   ├── 2026-08-02-vault-backup.zip
│   ├── 2026-08-03-vault-backup.zip
│   └── ...
├── Logs/
│   ├── queries-2026-08-02.log
│   ├── system-2026-08-02.log
│   └── ...
└── Config/
    ├── hermes-config.json
    └── models.json
```

## Performance

**Logging Overhead:**
- Notion: ~200ms per query
- Google Drive: ~500ms for backups
- Slack: ~100ms per notification

**Recommendations:**
- Async logging (don't block user)
- Batch writes to Notion
- Schedule backups during off-peak

## Security

### Data Privacy
- Queries stored in Notion (your account)
- Backups to Google Drive (encrypted)
- Slack notifications are real-time only

### Limitations
- No query retention on Slack (24-72 hour history)
- Notion data subject to your workspace retention
- Google Drive respects your storage quota

## Troubleshooting

### Notion Connection Failed
```bash
# Check Notion database exists
# Verify database ID in config
# Check write permissions
```

### Slack Not Receiving Messages
```bash
# Verify bot token is valid
# Check channel names match config
# Confirm bot has channel permissions
```

### Google Drive Backup Slow
```bash
# Check file size
# Verify internet connection
# Consider backup frequency/timing
```

## Future Enhancements

- [ ] Email digest via Gmail MCP
- [ ] Teams integration for notifications
- [ ] Airtable for structured query logging
- [ ] Real-time Slack slash commands
- [ ] Google Sheets analytics dashboard

## Testing

Run MCP tests:
```bash
node tests/mcp-test.js
```

This validates all three services are accessible and working.

---

**Status**: Integration Foundation Complete  
**Next Phase**: Production MCP API Integration  
**Last Updated**: 2026-08-02

# Telegram Integration for Claude Code via Hermes

Send instructions, prompts, images, and code from Telegram to Claude Code using Nous Hermes as a bridge.

## Quick Start

1. **Ensure Hermes is running** at `100.86.232.77:8080`
2. **MCP is configured** in `.claude/settings.json` (already done)
3. **Send a message to @Danrcbh_bot** on Telegram
4. **Claude Code receives** the message through Hermes MCP

## What You Can Do

| Telegram Input | Claude Code | Result |
|---|---|---|
| Text prompt | /claude "task" | Claude processes the prompt |
| Code block | /code {...} | Code is executed/reviewed |
| Image/Screenshot | Send image | Analyzed by Claude with vision |
| File | Send file | File content available to Claude |
| Instructions | Natural text | Creates tasks in Claude Code |

## How It Works

```
You (Telegram)
    ↓ @Danrcbh_bot
Hermes Agent (MCP Server)
    ↓ 100.86.232.77:8080
Claude Code
    ↓ Response
Back to Telegram
```

## Configuration

The integration uses:
- **Hermes Token**: Already connected via MCP
- **Bot Token**: `8913080097:AAGaQaB0hFSK-sPyjNxn0f62mqjZIW9aQXI`
- **Server**: `100.86.232.77:8080`
- **MCP Settings**: `.claude/settings.json`

## Key Files

- `TELEGRAM_INTEGRATION.md` - Detailed setup and architecture
- `.claude/settings.json` - MCP server configuration
- This file - Project overview

## Testing

Send a test message to @Danrcbh_bot:
```
Test message to verify Claude Code integration
```

Check Claude Code receives it and can respond.

## Support

For issues:
1. Verify Hermes server health: `curl http://100.86.232.77:8080/health`
2. Check MCP connection in `.claude/settings.json`
3. Review Telegram bot permissions
4. Check Hermes logs for message processing

See `TELEGRAM_INTEGRATION.md` for detailed troubleshooting.

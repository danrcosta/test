# Telegram Integration via Hermes

This integration allows you to send instructions, prompts, images, and code from Telegram directly to Claude Code using the Hermes agent as a bridge.

## Architecture

```
Telegram Bot (@Danrcbh_bot)
        ↓
    Hermes MCP Server (100.86.232.77:8080)
        ↓
    Claude Code Sessions
```

## Setup

### 1. Hermes MCP Connection
The `.claude/settings.json` is already configured to connect to your Hermes server at `100.86.232.77:8080`.

### 2. Telegram Bot Configuration
- **Bot Handle**: @Danrcbh_bot
- **Bot Token**: `$TELEGRAM_BOT_TOKEN`
- **Token Purpose**: Bridge between Telegram and Hermes

### 3. Usage

#### Send Text Instructions
```
/claude "Your instruction or prompt here"
```

#### Send Code
```
/code
<your code here>
```

#### Send Images
Just send images to the bot - they'll be captured and made available to Claude Code.

#### Send Files
Send any file to the bot - attachments are processed by Hermes and passed to Claude.

## Hermes Integration

The Hermes agent handles:
- **Message Routing**: Receives Telegram messages and routes them to Claude Code
- **Media Processing**: Extracts images, files, and code from messages
- **Context Preservation**: Maintains conversation context across sessions
- **Response Forwarding**: Sends Claude's responses back to Telegram

## Features

✅ Send prompts and instructions from Telegram
✅ Upload images and screenshots
✅ Share code snippets
✅ Receive responses in Telegram
✅ Conversation history tracking
✅ Multi-session support

## Architecture Flow

1. **User sends message to Telegram bot**
   ```
   Message → @Danrcbh_bot
   ```

2. **Hermes processes the message**
   ```
   Hermes receives via Telegram API
   → Extracts content (text, images, files)
   → Formats as Claude-compatible input
   ```

3. **Claude Code receives via MCP**
   ```
   Hermes MCP → Claude Code session
   → Processes prompt/code/image
   → Generates response
   ```

4. **Response sent back to Telegram**
   ```
   Claude response → Hermes
   → Formats message
   → Sends to Telegram bot
   → Delivered to user
   ```

## Environment

- **Hermes Server**: `100.86.232.77:8080`
- **Telegram Bot**: `@Danrcbh_bot`
- **Protocol**: MCP (Model Context Protocol)

## Testing

To verify the integration is working:

1. Send a test message to @Danrcbh_bot on Telegram
2. Check that Hermes receives it (logs at 100.86.232.77:8080)
3. Verify Claude Code receives the message via MCP
4. Confirm response is sent back to Telegram

## Troubleshooting

### Hermes Not Responding
- Verify server is running: `curl http://100.86.232.77:8080/health`
- Check network connectivity
- Verify bot token is active

### Messages Not Reaching Claude Code
- Check `.claude/settings.json` MCP configuration
- Verify Hermes MCP server command is correct
- Review MCP server logs

### Responses Not Reaching Telegram
- Verify bot token is still valid
- Check Telegram bot permissions
- Ensure Hermes has write access to Telegram API

## Next Steps

1. Test the integration with a simple message
2. Monitor Hermes logs for message processing
3. Customize message routing in Hermes as needed
4. Set up additional Telegram commands if desired

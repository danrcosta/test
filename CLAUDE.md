# Telegram Integration for Claude Code via Hermes

Send instructions, prompts, images, and code from Telegram to Claude Code
using Nous Hermes as a bridge.

## Quick Start

1. **Ensure Hermes is running** at the host in `HERMES_URL`
2. **Copy `.env.example` to `.env`** and fill in `TELEGRAM_BOT_TOKEN`
3. **Run the webhook server**: `python telegram_webhook_server.py`
4. **Send a message to your bot** on Telegram

## What You Can Do

| Telegram Input | Handler | Result |
|---|---|---|
| Text prompt | `process_text_message` | Forwarded to Hermes as a text prompt |
| `/code ...` | `process_code_command` | Forwarded to Hermes as a code snippet |
| Image/Screenshot | `process_photo_message` | Downloaded, base64-encoded, forwarded |
| File | `process_document_message` | Downloaded, read, forwarded |

## How It Works

```
You (Telegram)
    ↓ bot webhook
telegram_webhook_server.py  (FastAPI, port 8000)
    ↓ HTTP POST /claude/send
Hermes Agent
    ↓
Claude Code
```

## Configuration

All credentials come from the environment. See `.env.example` for the full
list. `.env` is gitignored — **never commit a real token**.

| Variable | Purpose |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot credential from @BotFather. Required. |
| `TELEGRAM_WEBHOOK_SECRET` | Shared secret for webhook request validation. |
| `HERMES_URL` | Hermes server base URL. |
| `GITHUB_ACCESS_TOKEN` | Token with `repo` scope for `hermes_github_automation.py`. |

## Status

Honest state of each component, so you know what you can rely on:

| Component | State |
|---|---|
| `obsidian_vault_manager.py` | Working. Local JSON+Markdown session store. |
| `telegram_webhook_server.py` | Working. See "Known gaps" below. |
| `hermes_claude_bridge.py` | HTTP client is real; the `/claude/send` endpoint has not been verified against a live Hermes server. |
| `telegram_hermes_obsidian_integrator.py` | Working glue between the two above. |
| `hermes_github_automation.py` | Real GitHub REST API client. Requires `GITHUB_ACCESS_TOKEN`. |
| `hermes_github_obsidian_bridge.py` | Logs real GitHub outcomes (success *and* failure) to the vault. |

### Known gaps

- **The webhook has no request validation.** It does not check the
  `X-Telegram-Bot-Api-Secret-Token` header and has no `chat_id` allowlist,
  so anyone who learns the URL can POST forged updates. `TELEGRAM_WEBHOOK_SECRET`
  exists in `.env.example` but is not yet enforced in the handler.
- **`POST /set-webhook` is unauthenticated** and can redirect where Telegram
  delivers updates.
- **No MCP server is configured.** Hermes is reached over plain HTTP by
  `hermes_claude_bridge.py`, not through MCP. See `.claude/settings.json`.
- **There are no automated tests.** No `test_*.py` files exist; the `main()`
  functions are manual smoke checks.

## Key Files

- `TELEGRAM_INTEGRATION.md` - Detailed setup and architecture
- `.claude/settings.json` - Claude Code permissions
- This file - Project overview

## Support

For issues:
1. Verify Hermes health: `curl "$HERMES_URL/health"`
2. Confirm `TELEGRAM_BOT_TOKEN` is set in the environment
3. Check the webhook is registered: `getWebhookInfo` on the Telegram API
4. Check Hermes logs for message processing

See `TELEGRAM_INTEGRATION.md` for detailed troubleshooting.

#!/usr/bin/env python3
"""
Telegram Webhook Server
Receives messages from Telegram bot and forwards to Claude Code via Hermes
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
import logging
import os
from datetime import datetime
from typing import Optional
import json
from hermes_claude_bridge import HermesClaudeBridge, ContentType
from pathlib import Path
import aiohttp
import asyncio

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Telegram to Claude Bridge")

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError(
        "TELEGRAM_BOT_TOKEN is not set. Export it or put it in a .env file "
        "(which is gitignored) — never hardcode it in this file."
    )
TELEGRAM_API_URL = "https://api.telegram.org/bot"
HERMES_URL = os.getenv("HERMES_URL", "http://100.86.232.77:8080")
WEBHOOK_PATH = "/webhook/telegram"
MEDIA_CACHE_DIR = Path("./telegram_media_cache")

# Create media cache directory
MEDIA_CACHE_DIR.mkdir(exist_ok=True)

# Initialize Hermes bridge
hermes_bridge = HermesClaudeBridge(hermes_url=HERMES_URL)


class TelegramMessageHandler:
    """Handle incoming Telegram messages"""

    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.api_url = f"{TELEGRAM_API_URL}{bot_token}"

    async def get_file(self, file_id: str) -> Optional[str]:
        """Download file from Telegram"""
        try:
            # Get file info
            response = requests.get(
                f"{self.api_url}/getFile",
                params={"file_id": file_id}
            )

            if response.status_code != 200:
                logger.error(f"Failed to get file info: {response.text}")
                return None

            file_info = response.json()["result"]
            file_path = file_info["file_path"]

            # Download file
            file_url = f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"
            file_response = requests.get(file_url)

            if file_response.status_code != 200:
                logger.error(f"Failed to download file")
                return None

            # Save to cache
            cache_path = MEDIA_CACHE_DIR / Path(file_path).name
            with open(cache_path, 'wb') as f:
                f.write(file_response.content)

            logger.info(f"✅ File downloaded: {cache_path}")
            return str(cache_path)

        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return None

    async def send_message(self, chat_id: int, text: str):
        """Send message back to Telegram"""
        try:
            response = requests.post(
                f"{self.api_url}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "HTML"
                }
            )
            if response.status_code == 200:
                logger.info(f"✅ Message sent to chat {chat_id}")
            else:
                logger.error(f"Failed to send message: {response.text}")
        except Exception as e:
            logger.error(f"Error sending message: {e}")


async def process_text_message(update: dict, handler: TelegramMessageHandler):
    """Process text message"""
    chat_id = update["message"]["chat"]["id"]
    user_id = update["message"]["from"]["id"]
    username = update["message"]["from"].get("username", "unknown")
    text = update["message"]["text"]

    logger.info(f"📝 Text from @{username}: {text[:50]}...")

    metadata = {
        "source": "telegram",
        "user": username,
        "user_id": user_id,
        "chat_id": chat_id,
        "message_type": "text"
    }

    result = hermes_bridge.send_text_prompt(text, metadata=metadata)

    # Send response back to Telegram
    if result["success"]:
        response_text = "✅ Mensagem enviada para Claude Code com sucesso!"
    else:
        response_text = f"❌ Erro: {result.get('error', 'Unknown error')}"

    await handler.send_message(chat_id, response_text)


async def process_photo_message(update: dict, handler: TelegramMessageHandler):
    """Process photo message"""
    chat_id = update["message"]["chat"]["id"]
    user_id = update["message"]["from"]["id"]
    username = update["message"]["from"].get("username", "unknown")
    caption = update["message"].get("caption", "")

    # Get the largest photo
    photos = update["message"]["photo"]
    file_id = photos[-1]["file_id"]

    logger.info(f"🖼️  Photo from @{username}")

    # Download photo
    image_path = await handler.get_file(file_id)

    if not image_path:
        await handler.send_message(chat_id, "❌ Erro ao baixar imagem")
        return

    metadata = {
        "source": "telegram",
        "user": username,
        "user_id": user_id,
        "chat_id": chat_id,
        "message_type": "photo",
        "caption": caption
    }

    result = hermes_bridge.send_image_analysis(
        image_path=image_path,
        description=caption or "Analyze this Telegram image",
        metadata=metadata
    )

    if result["success"]:
        response_text = "✅ Imagem enviada para Claude Code!"
    else:
        response_text = f"❌ Erro: {result.get('error', 'Unknown error')}"

    await handler.send_message(chat_id, response_text)


async def process_document_message(update: dict, handler: TelegramMessageHandler):
    """Process document/file message"""
    chat_id = update["message"]["chat"]["id"]
    user_id = update["message"]["from"]["id"]
    username = update["message"]["from"].get("username", "unknown")

    document = update["message"]["document"]
    file_id = document["file_id"]
    filename = document.get("file_name", "file")

    logger.info(f"📄 Document from @{username}: {filename}")

    # Download file
    file_path = await handler.get_file(file_id)

    if not file_path:
        await handler.send_message(chat_id, "❌ Erro ao baixar arquivo")
        return

    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        with open(file_path, 'rb') as f:
            content = f.read().decode('utf-8', errors='ignore')

    metadata = {
        "source": "telegram",
        "user": username,
        "user_id": user_id,
        "chat_id": chat_id,
        "message_type": "document",
        "filename": filename
    }

    result = hermes_bridge.send_file(
        file_path=file_path,
        content=content,
        metadata=metadata
    )

    if result["success"]:
        response_text = f"✅ Arquivo '{filename}' enviado para Claude Code!"
    else:
        response_text = f"❌ Erro: {result.get('error', 'Unknown error')}"

    await handler.send_message(chat_id, response_text)


async def process_code_command(update: dict, handler: TelegramMessageHandler):
    """Process /code command"""
    chat_id = update["message"]["chat"]["id"]
    user_id = update["message"]["from"]["id"]
    username = update["message"]["from"].get("username", "unknown")

    # Get text after /code
    text = update["message"]["text"]
    code = text.replace("/code", "").strip()

    if not code:
        await handler.send_message(chat_id, "⚠️ Use: /code <seu_codigo>")
        return

    logger.info(f"💻 Code from @{username}")

    metadata = {
        "source": "telegram",
        "user": username,
        "user_id": user_id,
        "chat_id": chat_id,
        "message_type": "code",
        "language": "text"
    }

    result = hermes_bridge.send_code(code, metadata=metadata)

    if result["success"]:
        response_text = "✅ Código enviado para Claude Code!"
    else:
        response_text = f"❌ Erro: {result.get('error', 'Unknown error')}"

    await handler.send_message(chat_id, response_text)


@app.post(WEBHOOK_PATH)
async def webhook(request: Request):
    """Webhook endpoint for Telegram"""
    try:
        update = await request.json()
        logger.info(f"📨 Received update: {json.dumps(update, indent=2)[:200]}...")

        if "message" not in update:
            return JSONResponse({"ok": True})

        message = update["message"]
        handler = TelegramMessageHandler(TELEGRAM_BOT_TOKEN)

        # Route message types
        if "text" in message:
            text = message["text"]
            if text.startswith("/code"):
                await process_code_command(update, handler)
            else:
                await process_text_message(update, handler)

        elif "photo" in message:
            await process_photo_message(update, handler)

        elif "document" in message:
            await process_document_message(update, handler)

        else:
            logger.info(f"⚠️ Unsupported message type: {message.keys()}")

        return JSONResponse({"ok": True})

    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}", exc_info=True)
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.get("/health")
async def health():
    """Health check endpoint"""
    hermes_healthy = hermes_bridge.health_check()
    return {
        "status": "healthy" if hermes_healthy else "unhealthy",
        "hermes": "connected" if hermes_healthy else "disconnected",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Telegram to Claude Code Bridge",
        "version": "1.0",
        "webhook_path": WEBHOOK_PATH,
        "status": "running"
    }


@app.post("/set-webhook")
async def set_webhook(webhook_url: str):
    """Set webhook URL on Telegram"""
    try:
        handler = TelegramMessageHandler(TELEGRAM_BOT_TOKEN)
        response = requests.post(
            f"{handler.api_url}/setWebhook",
            json={"url": webhook_url}
        )

        if response.status_code == 200:
            logger.info(f"✅ Webhook set to: {webhook_url}")
            return {"ok": True, "message": "Webhook configured"}
        else:
            logger.error(f"Failed to set webhook: {response.text}")
            return {"ok": False, "error": response.text}
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return {"ok": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("WEBHOOK_PORT", 8000))
    host = os.getenv("WEBHOOK_HOST", "0.0.0.0")

    logger.info(f"🚀 Starting Telegram Webhook Server on {host}:{port}")
    logger.info(f"📍 Webhook path: {WEBHOOK_PATH}")
    logger.info(f"🤖 Bot token configured: {TELEGRAM_BOT_TOKEN[:10]}...")

    uvicorn.run(app, host=host, port=port)

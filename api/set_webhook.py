"""Vercel serverless function: One-time webhook registration.

Hit GET /api/set_webhook after deploying to register the webhook URL
with Telegram.

Usage after deploy:
    curl https://your-project.vercel.app/api/set_webhook
"""

import os
import sys
import json
import asyncio
import logging

from flask import Flask, Response, request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Bot
from config.settings import BOT_TOKEN, validate_env

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_webhook_url():
    """Determine the public webhook URL."""
    explicit = os.getenv("WEBHOOK_URL")
    if explicit:
        return explicit.rstrip("/") + "/api/webhook"

    vercel_url = os.getenv("VERCEL_URL")
    if vercel_url:
        return f"https://{vercel_url}/api/webhook"

    return None


async def _set_webhook():
    validate_env()
    url = _get_webhook_url()
    if not url:
        return {"ok": False, "error": "Cannot determine webhook URL. Set WEBHOOK_URL env var."}

    bot = Bot(token=BOT_TOKEN)
    async with bot:
        await bot.set_webhook(url=url, allowed_updates=["message", "callback_query"])
        info = await bot.get_webhook_info()

    return {
        "ok": True,
        "webhook_url": info.url,
        "pending_update_count": info.pending_update_count,
        "max_connections": info.max_connections,
    }


async def _delete_webhook():
    validate_env()
    bot = Bot(token=BOT_TOKEN)
    async with bot:
        await bot.delete_webhook()
    return {"ok": True, "message": "Webhook deleted."}


async def _get_info():
    validate_env()
    bot = Bot(token=BOT_TOKEN)
    async with bot:
        info = await bot.get_webhook_info()
    return {
        "ok": True,
        "webhook_url": info.url or "(none)",
        "pending_update_count": info.pending_update_count,
    }


app = Flask(__name__)


@app.route("/api/set_webhook", methods=["GET"])
def set_webhook():
    """
    GET /api/set_webhook             -> register webhook
    GET /api/set_webhook?action=delete   -> remove webhook
    GET /api/set_webhook?action=info     -> show status
    """
    action = request.args.get("action", "set")

    try:
        if action == "delete":
            result = asyncio.run(_delete_webhook())
        elif action == "info":
            result = asyncio.run(_get_info())
        else:
            result = asyncio.run(_set_webhook())
    except Exception as e:
        logger.exception("set_webhook error")
        result = {"ok": False, "error": str(e)}

    return Response(
        json.dumps(result, indent=2),
        status=200,
        content_type="application/json",
    )

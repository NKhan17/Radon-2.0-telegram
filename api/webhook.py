"""Vercel serverless function: Telegram webhook endpoint.

Telegram POSTs updates to /api/webhook. This function processes each
update through the same Application and handler stack used in polling
mode, with MongoDB-backed persistence for ConversationHandler state.
"""

import os
import sys
import json
import asyncio
import logging

from flask import Flask, Response, request

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update
from config.settings import BOT_TOKEN, validate_env
from bot_app import build_application

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Build application once at module level (persists across warm invocations)
validate_env()
_app = build_application(use_persistence=True, use_updater=False)
_initialized = False


async def _ensure_init():
    global _initialized
    if not _initialized:
        await _app.initialize()
        _initialized = True


async def _process_update(body: dict):
    await _ensure_init()
    update = Update.de_json(body, _app.bot)
    await _app.process_update(update)


# Flask app
app = Flask(__name__)


@app.route("/api/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        asyncio.run(_process_update(data))
    except Exception:
        logger.exception("Error processing webhook update")
    # Always return 200 so Telegram does not retry
    return Response("OK", status=200)


@app.route("/api/webhook", methods=["GET"])
def health():
    return Response(
        json.dumps({"status": "ok", "bot": "Radon 2.0"}),
        status=200,
        content_type="application/json",
    )

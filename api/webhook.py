"""Vercel serverless function: Telegram webhook endpoint.

Telegram POSTs updates to /api/webhook. This function processes each
update through the same Application and handler stack used in polling mode,
but with MongoDB-backed persistence so ConversationHandler state survives
cold starts.
"""

import sys
import os
import json
import asyncio
import logging
from http.server import BaseHTTPRequestHandler

# Vercel runs the function from the repo root, so make sure the project
# root is on sys.path for absolute imports (config, commands, etc.)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update
from config.settings import BOT_TOKEN, validate_env
from bot_app import build_application

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── Global application (persists across warm invocations) ──────────────
validate_env()
_app = build_application(use_persistence=True, use_updater=False)
_initialized = False


async def _ensure_init():
    """Initialize the Application exactly once (survives warm invocations)."""
    global _initialized
    if not _initialized:
        await _app.initialize()
        _initialized = True


async def _process_update(body: bytes):
    """Parse the raw webhook body and dispatch through handlers."""
    await _ensure_init()
    data = json.loads(body)
    update = Update.de_json(data, _app.bot)
    await _app.process_update(update)


class handler(BaseHTTPRequestHandler):
    """Vercel entry-point. Class MUST be named ``handler``."""

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            # Run the async processing inside a new or existing event loop
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                # Shouldn't normally happen in Vercel, but be safe
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    pool.submit(asyncio.run, _process_update(body)).result()
            else:
                asyncio.run(_process_update(body))

            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception:
            logger.exception("Error processing webhook update")
            self.send_response(200)  # Always 200 so Telegram doesn't retry
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ERROR")

    def do_GET(self):
        """Health-check / keep-alive endpoint."""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok", "bot": "Radon 2.0"}).encode())

    def log_message(self, format, *args):
        """Suppress default stderr logging; we use Python logging instead."""
        logger.info(format % args)

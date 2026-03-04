"""Render Free Web Service entry point.

Runs the Telegram polling bot in a background thread alongside a lightweight
aiohttp HTTP server. The HTTP server lets Render treat this as a Web Service
(which has a free tier) rather than a Background Worker (which doesn't).

Point UptimeRobot or any cron pinger at your Render URL every 5 minutes
to prevent the free instance from spinning down due to inactivity.
"""

import asyncio
import logging
import threading

from aiohttp import web
from telegram import Update

from config.settings import validate_env
from bot_app import build_application, BOT_COMMANDS

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Telegram bot — runs in its own thread via run_polling (blocking)
# ---------------------------------------------------------------------------

def run_bot():
    """Start the Telegram bot in polling mode (blocking call in its own thread)."""
    validate_env()

    async def post_init(application):
        await application.bot.set_my_commands(BOT_COMMANDS)
        logger.info("Bot commands registered with Telegram.")
        logger.info("Radon 2.0 Telegram Edition is online! (polling mode)")

    app = build_application(use_persistence=False, use_updater=True)
    app.post_init = post_init

    logger.info("Starting Radon 2.0 polling (poll_interval=0.5s)...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, poll_interval=0.5)


# ---------------------------------------------------------------------------
# aiohttp web server — satisfies Render's port-binding requirement
# ---------------------------------------------------------------------------

async def health(request):
    return web.Response(text="Radon 2.0 is running.", content_type="text/plain")


async def run_web_server():
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)

    runner = web.AppRunner(app)
    await runner.setup()

    # Render injects PORT; default to 8080 for local testing
    import os
    port = int(os.environ.get("PORT", 8080))

    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Health-check server running on port {port}")

    # Keep running until cancelled
    while True:
        await asyncio.sleep(3600)


# ---------------------------------------------------------------------------
# Main — wire both together
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Start the bot in a daemon thread so it doesn't block the event loop
    bot_thread = threading.Thread(target=run_bot, daemon=True, name="telegram-bot")
    bot_thread.start()

    # Run the web server on the main thread's event loop
    asyncio.run(run_web_server())

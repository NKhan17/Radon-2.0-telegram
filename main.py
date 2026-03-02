"""Entry point for local polling mode.

Usage:
    python main.py
"""

import logging
from telegram import Update
from config.settings import validate_env
from bot_app import build_application, BOT_COMMANDS

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def post_init(application):
    """Register bot commands with Telegram after startup."""
    await application.bot.set_my_commands(BOT_COMMANDS)
    logger.info("Bot commands registered with Telegram.")
    logger.info("Radon 2.0 Telegram Edition is online! (polling mode)")


def main():
    validate_env()

    app = build_application(use_persistence=False, use_updater=True)
    app.post_init = post_init

    logger.info("Starting Radon 2.0 polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

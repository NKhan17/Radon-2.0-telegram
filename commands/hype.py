from html import escape
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def hype(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the official Radon workout playlist link."""
    playlist_url = "https://music.youtube.com/playlist?list=PLiOIgEQJFWM75NepWUZEVG8U2fKhqRoOf"

    text = (
        "<b>Radon Hype Mix</b>\n\n"
        "Fuel your workout with the official training playlist.\n\n"
        f"<b>Listen on YouTube Music</b>\n"
        f'<a href="{escape(playlist_url)}">Click here to start the grind</a>\n\n'
        "<i>No excuses. Let's get to work.</i>"
    )

    await update.message.reply_text(text, parse_mode="HTML", disable_web_page_preview=True)

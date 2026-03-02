import logging
from telegram import BotCommand, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from config.settings import BOT_TOKEN, validate_env
from commands import (
    workout,
    custom_workout,
    diet,
    flex,
    fun,
    hype,
    moderation,
    tag,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    text = (
        "<b>Radon 2.0 - Telegram Edition</b>\n\n"
        "Your fitness companion bot. Use /help to see all available commands.\n\n"
        "<i>YOLO /startworkout</i>"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    text = (
        "<b>Radon 2.0 Commands</b>\n\n"

        "<b>Workout</b>\n"
        "/schedule - View the weekly training split\n"
        "/startworkout - Start your level-based routine\n"
        "/myworkout - View/edit your custom workout list\n\n"

        "<b>Nutrition</b>\n"
        "/diet - Browse the nutritional food guide\n\n"

        "<b>Progress</b>\n"
        "/flex - View/edit your progress log\n\n"

        "<b>Fun</b>\n"
        "/rps - Rock Paper Scissors\n"
        "/meme - Get a random meme\n"
        "/eightball - Ask the magic 8-ball\n"
        "/dadjoke - Get a dad joke\n"
        "/hype - Official workout playlist\n\n"

        "<b>Tags</b>\n"
        "/tag - Manage chat tags (create/get/delete/list)\n\n"

        "<b>Moderation</b> (admin only)\n"
        "/purge - Delete recent messages\n"
        "/kick - Kick a user\n"
        "/ban - Ban a user\n"
        "/unban - Unban a user by ID\n\n"

        "<i>Use /cancel to exit any multi-step input.</i>"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def noop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle noop callback (pagination page counter button)."""
    await update.callback_query.answer()


async def post_init(application):
    """Register bot commands with Telegram after startup."""
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Show all commands"),
        BotCommand("schedule", "View weekly training split"),
        BotCommand("startworkout", "Start your workout routine"),
        BotCommand("myworkout", "View/edit custom workout list"),
        BotCommand("diet", "Browse nutritional food guide"),
        BotCommand("flex", "View/edit your progress log"),
        BotCommand("rps", "Rock Paper Scissors"),
        BotCommand("meme", "Get a random meme"),
        BotCommand("eightball", "Ask the magic 8-ball"),
        BotCommand("dadjoke", "Get a dad joke"),
        BotCommand("hype", "Official workout playlist"),
        BotCommand("tag", "Manage chat tags"),
        BotCommand("purge", "Delete recent messages (admin)"),
        BotCommand("kick", "Kick a user (admin)"),
        BotCommand("ban", "Ban a user (admin)"),
        BotCommand("unban", "Unban a user by ID (admin)"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands registered with Telegram.")
    logger.info("Radon 2.0 Telegram Edition is online!")


def main():
    validate_env()

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    # --- ConversationHandlers (must be registered before generic CallbackQueryHandlers) ---
    app.add_handler(custom_workout.myworkout_add_conv)
    app.add_handler(custom_workout.myworkout_del_conv)
    app.add_handler(flex.flex_add_conv)
    app.add_handler(flex.flex_del_conv)

    # --- Command Handlers ---
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("schedule", workout.schedule))
    app.add_handler(CommandHandler("startworkout", workout.startworkout))
    app.add_handler(CommandHandler("myworkout", custom_workout.myworkout))
    app.add_handler(CommandHandler("diet", diet.diet))
    app.add_handler(CommandHandler("flex", flex.flex))
    app.add_handler(CommandHandler("rps", fun.rps))
    app.add_handler(CommandHandler("meme", fun.meme))
    app.add_handler(CommandHandler("eightball", fun.eightball))
    app.add_handler(CommandHandler("dadjoke", fun.dadjoke))
    app.add_handler(CommandHandler("hype", hype.hype))
    app.add_handler(CommandHandler("tag", tag.tag))
    app.add_handler(CommandHandler("purge", moderation.purge))
    app.add_handler(CommandHandler("kick", moderation.kick))
    app.add_handler(CommandHandler("ban", moderation.ban))
    app.add_handler(CommandHandler("unban", moderation.unban))

    # --- Callback Query Handlers ---
    app.add_handler(CallbackQueryHandler(noop_callback, pattern=r"^noop$"))
    app.add_handler(CallbackQueryHandler(workout.workout_callback, pattern=r"^wo:"))
    app.add_handler(CallbackQueryHandler(diet.diet_callback, pattern=r"^diet:"))
    app.add_handler(CallbackQueryHandler(fun.rps_callback, pattern=r"^rps:"))
    app.add_handler(CallbackQueryHandler(flex.flex_callback, pattern=r"^fx:"))
    app.add_handler(CallbackQueryHandler(custom_workout.mw_callback, pattern=r"^mw:"))

    # --- Message tracker for /purge (high group number so it runs alongside everything) ---
    app.add_handler(moderation.message_tracker, group=1)

    # --- Error handler ---
    async def error_handler(update, context):
        logger.error("Exception while handling an update:", exc_info=context.error)

    app.add_error_handler(error_handler)

    logger.info("Starting Radon 2.0 polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

import random
from html import escape
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.api_client import fetch_dad_joke


# --- Rock Paper Scissors ---

async def rps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start a Rock Paper Scissors game."""
    user_id = update.effective_user.id
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Rock", callback_data=f"rps:rock:{user_id}"),
            InlineKeyboardButton("Paper", callback_data=f"rps:paper:{user_id}"),
            InlineKeyboardButton("Scissors", callback_data=f"rps:scissors:{user_id}"),
        ]
    ])
    text = "<b>Rock Paper Scissors</b>\n\nChoose your weapon below!"
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")


async def rps_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Rock Paper Scissors button presses."""
    query = update.callback_query
    parts = query.data.split(":")
    # rps:choice:user_id
    user_choice = parts[1].capitalize()
    owner_id = int(parts[2])

    if query.from_user.id != owner_id:
        await query.answer("This isn't your game!", show_alert=True)
        return

    await query.answer()

    choices = ["Rock", "Paper", "Scissors"]
    bot_choice = random.choice(choices)

    if user_choice == bot_choice:
        result = "It's a <b>Tie</b>!"
    elif (
        (user_choice == "Rock" and bot_choice == "Scissors")
        or (user_choice == "Paper" and bot_choice == "Rock")
        or (user_choice == "Scissors" and bot_choice == "Paper")
    ):
        result = "You <b>Won</b>!"
    else:
        result = "You <b>Lost</b>!"

    text = (
        f"<b>Rock Paper Scissors</b>\n\n"
        f"<b>Your Choice:</b> {escape(user_choice)}\n"
        f"<b>Radon's Choice:</b> {escape(bot_choice)}\n\n"
        f"{result}"
    )

    await query.edit_message_text(text, parse_mode="HTML", reply_markup=None)




# --- 8-Ball ---

EIGHTBALL_RESPONSES = [
    "Yes, obviously.",
    "My sources say... maybe. If you stop being annoying.",
    "Ask again when you've gained some muscle.",
    "Don't count on it, buddy.",
    "Signs point to yes.",
    "Cannot predict now, I'm at the gym.",
    "Outlook not so good.",
    "Very doubtful.",
    "Yes, but it'll cost you.",
]


async def eightball(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Magic 8-ball with snarky responses."""
    question = " ".join(context.args) if context.args else ""
    if not question:
        await update.message.reply_text("Please ask a question: <code>/eightball Will I pass?</code>", parse_mode="HTML")
        return

    answer = random.choice(EIGHTBALL_RESPONSES)
    text = (
        "<b>The Snarky 8-Ball</b>\n\n"
        f"<b>Question:</b> {escape(question)}\n\n"
        f"<b>Radon's Answer:</b> {escape(answer)}"
    )

    await update.message.reply_text(text, parse_mode="HTML")


# --- Dad Joke ---

async def dadjoke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and send a random dad joke."""
    joke = await fetch_dad_joke()
    if not joke:
        await update.message.reply_text("I'm not in a funny mood right now.")
        return

    await update.message.reply_text(f"{escape(joke)}", parse_mode="HTML")

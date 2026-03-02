from html import escape
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from services.database import custom_workouts

PER_PAGE = 5

# Conversation states
WAITING_EXERCISE_NAME = 0
WAITING_EXERCISE_REPS = 1
WAITING_DELETE_NUMBER = 2


def _build_myworkout_text(data, page, max_page, user_name):
    lines = [f"<b>{escape(user_name)}'s Private Armory</b>"]
    lines.append("<i>Your custom-crafted routine. Stay shielded, stay strong.</i>\n")

    if not data:
        lines.append("Empty. Use <b>Add</b> to forge your first exercise.")
    else:
        start = page * PER_PAGE
        page_items = data[start : start + PER_PAGE]
        for i, w in enumerate(page_items, start + 1):
            lines.append(f"<b>{i}. {escape(w['exercise'])}</b>\n   {escape(w['reps'])}")

    lines.append(f"\n<i>Page {page + 1} of {max_page + 1}</i>")
    return "\n".join(lines)


def _build_myworkout_keyboard(page, max_page, user_id):
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("< Prev", callback_data=f"mw:page:{page - 1}:{user_id}"))
    nav_row.append(InlineKeyboardButton(f"{page + 1}/{max_page + 1}", callback_data="noop"))
    if page < max_page:
        nav_row.append(InlineKeyboardButton("Next >", callback_data=f"mw:page:{page + 1}:{user_id}"))

    action_row = [
        InlineKeyboardButton("Add", callback_data=f"mw:add:{user_id}"),
        InlineKeyboardButton("Delete", callback_data=f"mw:del:{user_id}"),
        InlineKeyboardButton("Clear All", callback_data=f"mw:clr:{user_id}"),
    ]

    return InlineKeyboardMarkup([nav_row, action_row])


async def _get_user_data(user_id):
    doc = await custom_workouts.find_one({"_id": user_id})
    return doc.get("workouts", []) if doc else []


async def _send_myworkout_view(context, chat_id, message_id, user_id, user_name, page=0):
    data = await _get_user_data(user_id)
    max_page = max(0, (len(data) - 1) // PER_PAGE) if data else 0
    page = max(0, min(page, max_page))
    text = _build_myworkout_text(data, page, max_page, user_name)
    keyboard = _build_myworkout_keyboard(page, max_page, user_id)

    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )


# --- Command handler ---

async def myworkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View/Edit your custom private workout list."""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    data = await _get_user_data(user_id)
    max_page = max(0, (len(data) - 1) // PER_PAGE) if data else 0

    text = _build_myworkout_text(data, 0, max_page, user_name)
    keyboard = _build_myworkout_keyboard(0, max_page, user_id)

    await update.message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")


# --- Callback handler ---

async def mw_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle myworkout pagination, clear, and confirmation callbacks."""
    query = update.callback_query
    parts = query.data.split(":")

    if parts[0] == "noop":
        await query.answer()
        return

    action = parts[1]
    user_id = int(parts[-1])

    if query.from_user.id != user_id:
        await query.answer("This isn't your workout list!", show_alert=True)
        return

    await query.answer()

    if action == "page":
        page = int(parts[2])
        user_name = query.from_user.first_name
        data = await _get_user_data(user_id)
        max_page = max(0, (len(data) - 1) // PER_PAGE) if data else 0
        page = max(0, min(page, max_page))
        text = _build_myworkout_text(data, page, max_page, user_name)
        keyboard = _build_myworkout_keyboard(page, max_page, user_id)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")

    elif action == "clr":
        # Show confirmation
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Yes, clear all", callback_data=f"mw:clryes:{user_id}"),
                InlineKeyboardButton("Cancel", callback_data=f"mw:clrno:{user_id}"),
            ]
        ])
        await query.edit_message_text("Are you sure you want to clear all exercises?", reply_markup=keyboard)

    elif action == "clryes":
        await custom_workouts.update_one({"_id": user_id}, {"$set": {"workouts": []}})
        user_name = query.from_user.first_name
        text = _build_myworkout_text([], 0, 0, user_name)
        keyboard = _build_myworkout_keyboard(0, 0, user_id)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")

    elif action == "clrno":
        user_name = query.from_user.first_name
        data = await _get_user_data(user_id)
        max_page = max(0, (len(data) - 1) // PER_PAGE) if data else 0
        text = _build_myworkout_text(data, 0, max_page, user_name)
        keyboard = _build_myworkout_keyboard(0, max_page, user_id)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")


# --- ConversationHandler for Add ---

async def mw_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point: user pressed the Add button."""
    query = update.callback_query
    parts = query.data.split(":")
    user_id = int(parts[2])

    if query.from_user.id != user_id:
        await query.answer("This isn't your workout list!", show_alert=True)
        return ConversationHandler.END

    await query.answer()
    context.user_data["mw_message_id"] = query.message.message_id
    context.user_data["mw_chat_id"] = query.message.chat_id

    await query.edit_message_text("Type the <b>exercise name</b> (or /cancel):", parse_mode="HTML")
    return WAITING_EXERCISE_NAME


async def mw_add_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive exercise name, ask for reps."""
    context.user_data["mw_exercise_name"] = update.message.text.strip()
    await update.message.reply_text("Now type the <b>sets/reps</b> (e.g. 3x10) or /cancel:", parse_mode="HTML")
    return WAITING_EXERCISE_REPS


async def mw_add_reps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive reps, save to DB, refresh view."""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    exercise_name = context.user_data.get("mw_exercise_name", "Unknown")
    reps = update.message.text.strip()

    new_entry = {"exercise": f"{exercise_name}", "reps": reps}
    await custom_workouts.update_one(
        {"_id": user_id},
        {"$push": {"workouts": new_entry}},
        upsert=True,
    )

    data = await _get_user_data(user_id)
    max_page = max(0, (len(data) - 1) // PER_PAGE) if data else 0
    last_page = max_page
    text = _build_myworkout_text(data, last_page, max_page, user_name)
    keyboard = _build_myworkout_keyboard(last_page, max_page, user_id)

    # Edit the original list message
    chat_id = context.user_data.get("mw_chat_id")
    message_id = context.user_data.get("mw_message_id")
    if chat_id and message_id:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=keyboard,
                parse_mode="HTML",
            )
        except Exception:
            pass

    await update.message.reply_text(f"Added <b>{escape(exercise_name)}</b> ({escape(reps)})!", parse_mode="HTML")
    return ConversationHandler.END


# --- ConversationHandler for Delete ---

async def mw_del_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point: user pressed the Delete button."""
    query = update.callback_query
    parts = query.data.split(":")
    user_id = int(parts[2])

    if query.from_user.id != user_id:
        await query.answer("This isn't your workout list!", show_alert=True)
        return ConversationHandler.END

    await query.answer()
    context.user_data["mw_message_id"] = query.message.message_id
    context.user_data["mw_chat_id"] = query.message.chat_id

    await query.edit_message_text("Type the <b>exercise number</b> to delete (or /cancel):", parse_mode="HTML")
    return WAITING_DELETE_NUMBER


async def mw_del_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive the number, delete the exercise, refresh view."""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    val = update.message.text.strip()

    if not val.isdigit():
        await update.message.reply_text("Please enter a valid number.")
        return WAITING_DELETE_NUMBER

    idx = int(val) - 1
    data = await _get_user_data(user_id)

    if idx < 0 or idx >= len(data):
        await update.message.reply_text("Number not found. Try again or /cancel.")
        return WAITING_DELETE_NUMBER

    removed = data.pop(idx)
    await custom_workouts.update_one({"_id": user_id}, {"$set": {"workouts": data}})

    max_page = max(0, (len(data) - 1) // PER_PAGE) if data else 0
    text = _build_myworkout_text(data, 0, max_page, user_name)
    keyboard = _build_myworkout_keyboard(0, max_page, user_id)

    chat_id = context.user_data.get("mw_chat_id")
    message_id = context.user_data.get("mw_message_id")
    if chat_id and message_id:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=keyboard,
                parse_mode="HTML",
            )
        except Exception:
            pass

    await update.message.reply_text(f"Deleted <b>{escape(removed['exercise'])}</b>.", parse_mode="HTML")
    return ConversationHandler.END


# --- Cancel handler ---

async def mw_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the current conversation."""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    data = await _get_user_data(user_id)
    max_page = max(0, (len(data) - 1) // PER_PAGE) if data else 0
    text = _build_myworkout_text(data, 0, max_page, user_name)
    keyboard = _build_myworkout_keyboard(0, max_page, user_id)

    chat_id = context.user_data.get("mw_chat_id")
    message_id = context.user_data.get("mw_message_id")
    if chat_id and message_id:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=keyboard,
                parse_mode="HTML",
            )
        except Exception:
            pass

    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END


# Build ConversationHandlers

myworkout_add_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(mw_add_start, pattern=r"^mw:add:")],
    states={
        WAITING_EXERCISE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, mw_add_name)],
        WAITING_EXERCISE_REPS: [MessageHandler(filters.TEXT & ~filters.COMMAND, mw_add_reps)],
    },
    fallbacks=[CommandHandler("cancel", mw_cancel)],
    per_user=True,
    per_chat=True,
    name="myworkout_add",
)

myworkout_del_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(mw_del_start, pattern=r"^mw:del:")],
    states={
        WAITING_DELETE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, mw_del_number)],
    },
    fallbacks=[CommandHandler("cancel", mw_cancel)],
    per_user=True,
    per_chat=True,
    name="myworkout_del",
)

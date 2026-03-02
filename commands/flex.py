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
from services.database import user_flexes

PER_PAGE = 4

# Conversation states
FLEX_EXERCISE = 0
FLEX_RESULT = 1
FLEX_DELETE_NUMBER = 2


def _build_flex_text(data, page, max_page, user_name):
    lines = [f"<b>{escape(user_name)}'s Flex Log</b>\n"]

    if not data:
        lines.append("No flexes yet. Use <b>Add</b> to record your progress!")
    else:
        start = page * PER_PAGE
        page_items = data[start : start + PER_PAGE]
        for i, f in enumerate(page_items, start + 1):
            lines.append(f"<b>{i}. {escape(f['exercise'])}</b>\n   {escape(f['stat'])}")

    lines.append(f"\n<i>Page {page + 1} of {max_page + 1}</i>")
    return "\n".join(lines)


def _build_flex_keyboard(page, max_page, user_id):
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("< Prev", callback_data=f"fx:page:{page - 1}:{user_id}"))
    nav_row.append(InlineKeyboardButton(f"{page + 1}/{max_page + 1}", callback_data="noop"))
    if page < max_page:
        nav_row.append(InlineKeyboardButton("Next >", callback_data=f"fx:page:{page + 1}:{user_id}"))

    action_row = [
        InlineKeyboardButton("Add", callback_data=f"fx:add:{user_id}"),
        InlineKeyboardButton("Delete", callback_data=f"fx:del:{user_id}"),
        InlineKeyboardButton("Clear All", callback_data=f"fx:clr:{user_id}"),
    ]

    return InlineKeyboardMarkup([nav_row, action_row])


async def _get_flex_data(user_id):
    doc = await user_flexes.find_one({"_id": user_id})
    return doc.get("flexes", []) if doc else []


# --- Command handler ---

async def flex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show your progress log."""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    data = await _get_flex_data(user_id)
    max_page = max(0, (len(data) - 1) // PER_PAGE) if data else 0

    text = _build_flex_text(data, 0, max_page, user_name)
    keyboard = _build_flex_keyboard(0, max_page, user_id)

    await update.message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")


# --- Callback handler ---

async def flex_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle flex pagination, clear, and confirmation callbacks."""
    query = update.callback_query
    parts = query.data.split(":")

    if parts[0] == "noop":
        await query.answer()
        return

    action = parts[1]
    user_id = int(parts[-1])

    if query.from_user.id != user_id:
        await query.answer("Only the owner can interact with this!", show_alert=True)
        return

    await query.answer()

    if action == "page":
        page = int(parts[2])
        user_name = query.from_user.first_name
        data = await _get_flex_data(user_id)
        max_page = max(0, (len(data) - 1) // PER_PAGE) if data else 0
        page = max(0, min(page, max_page))
        text = _build_flex_text(data, page, max_page, user_name)
        keyboard = _build_flex_keyboard(page, max_page, user_id)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")

    elif action == "clr":
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Yes, clear all", callback_data=f"fx:clryes:{user_id}"),
                InlineKeyboardButton("Cancel", callback_data=f"fx:clrno:{user_id}"),
            ]
        ])
        await query.edit_message_text("Are you sure you want to clear all flex entries?", reply_markup=keyboard)

    elif action == "clryes":
        await user_flexes.update_one({"_id": user_id}, {"$set": {"flexes": []}})
        user_name = query.from_user.first_name
        text = _build_flex_text([], 0, 0, user_name)
        keyboard = _build_flex_keyboard(0, 0, user_id)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")

    elif action == "clrno":
        user_name = query.from_user.first_name
        data = await _get_flex_data(user_id)
        max_page = max(0, (len(data) - 1) // PER_PAGE) if data else 0
        text = _build_flex_text(data, 0, max_page, user_name)
        keyboard = _build_flex_keyboard(0, max_page, user_id)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")


# --- ConversationHandler for Add ---

async def fx_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry: user pressed Add button."""
    query = update.callback_query
    parts = query.data.split(":")
    user_id = int(parts[2])

    if query.from_user.id != user_id:
        await query.answer("Only the owner can add entries!", show_alert=True)
        return ConversationHandler.END

    await query.answer()
    context.user_data["fx_message_id"] = query.message.message_id
    context.user_data["fx_chat_id"] = query.message.chat_id

    await query.edit_message_text("Type the <b>exercise/skill name</b> (or /cancel):", parse_mode="HTML")
    return FLEX_EXERCISE


async def fx_add_exercise(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive exercise name, ask for result."""
    context.user_data["fx_exercise"] = update.message.text.strip()
    await update.message.reply_text("Now type the <b>result</b> (e.g. '15 seconds', '80kg') or /cancel:", parse_mode="HTML")
    return FLEX_RESULT


async def fx_add_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive result, save to DB, refresh view."""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    exercise = context.user_data.get("fx_exercise", "Unknown")
    stat = update.message.text.strip()

    new_entry = {"exercise": exercise, "stat": stat}
    await user_flexes.update_one(
        {"_id": user_id},
        {"$push": {"flexes": new_entry}},
        upsert=True,
    )

    data = await _get_flex_data(user_id)
    max_page = max(0, (len(data) - 1) // PER_PAGE) if data else 0
    last_page = max_page
    text = _build_flex_text(data, last_page, max_page, user_name)
    keyboard = _build_flex_keyboard(last_page, max_page, user_id)

    chat_id = context.user_data.get("fx_chat_id")
    message_id = context.user_data.get("fx_message_id")
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

    await update.message.reply_text(f"Recorded: <b>{escape(exercise)}</b> - {escape(stat)}", parse_mode="HTML")
    return ConversationHandler.END


# --- ConversationHandler for Delete ---

async def fx_del_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry: user pressed Delete button."""
    query = update.callback_query
    parts = query.data.split(":")
    user_id = int(parts[2])

    if query.from_user.id != user_id:
        await query.answer("Only the owner can delete entries!", show_alert=True)
        return ConversationHandler.END

    await query.answer()
    context.user_data["fx_message_id"] = query.message.message_id
    context.user_data["fx_chat_id"] = query.message.chat_id

    await query.edit_message_text("Type the <b>entry number</b> to delete (or /cancel):", parse_mode="HTML")
    return FLEX_DELETE_NUMBER


async def fx_del_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive the number, delete the entry, refresh view."""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    val = update.message.text.strip()

    if not val.isdigit():
        await update.message.reply_text("Please enter a valid number.")
        return FLEX_DELETE_NUMBER

    idx = int(val) - 1
    data = await _get_flex_data(user_id)

    if idx < 0 or idx >= len(data):
        await update.message.reply_text("Number not found. Try again or /cancel.")
        return FLEX_DELETE_NUMBER

    removed = data.pop(idx)
    await user_flexes.update_one({"_id": user_id}, {"$set": {"flexes": data}})

    max_page = max(0, (len(data) - 1) // PER_PAGE) if data else 0
    text = _build_flex_text(data, 0, max_page, user_name)
    keyboard = _build_flex_keyboard(0, max_page, user_id)

    chat_id = context.user_data.get("fx_chat_id")
    message_id = context.user_data.get("fx_message_id")
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

async def fx_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the current flex conversation."""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    data = await _get_flex_data(user_id)
    max_page = max(0, (len(data) - 1) // PER_PAGE) if data else 0
    text = _build_flex_text(data, 0, max_page, user_name)
    keyboard = _build_flex_keyboard(0, max_page, user_id)

    chat_id = context.user_data.get("fx_chat_id")
    message_id = context.user_data.get("fx_message_id")
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

flex_add_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(fx_add_start, pattern=r"^fx:add:")],
    states={
        FLEX_EXERCISE: [MessageHandler(filters.TEXT & ~filters.COMMAND, fx_add_exercise)],
        FLEX_RESULT: [MessageHandler(filters.TEXT & ~filters.COMMAND, fx_add_result)],
    },
    fallbacks=[CommandHandler("cancel", fx_cancel)],
    per_user=True,
    per_chat=True,
    name="flex_add",
)

flex_del_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(fx_del_start, pattern=r"^fx:del:")],
    states={
        FLEX_DELETE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, fx_del_number)],
    },
    fallbacks=[CommandHandler("cancel", fx_cancel)],
    per_user=True,
    per_chat=True,
    name="flex_del",
)

from html import escape
from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from services.database import tags
from helpers.permissions import admin_required


async def tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manage server tags. Usage: /tag <create|get|delete|list> [args]"""
    if not context.args:
        await update.message.reply_text(
            "<b>Tag Commands</b>\n\n"
            "<code>/tag create &lt;name&gt; &lt;content&gt;</code> - Create a tag\n"
            "<code>/tag get &lt;name&gt;</code> - View a tag\n"
            "<code>/tag delete &lt;name&gt;</code> - Delete a tag\n"
            "<code>/tag list</code> - List all tags",
            parse_mode="HTML",
        )
        return

    sub = context.args[0].lower()

    if sub == "create":
        await _tag_create(update, context)
    elif sub == "get":
        await _tag_get(update, context)
    elif sub == "delete":
        await _tag_delete(update, context)
    elif sub == "list":
        await _tag_list(update, context)
    else:
        await update.message.reply_text(
            f"Unknown subcommand <code>{escape(sub)}</code>. Use create, get, delete, or list.",
            parse_mode="HTML",
        )


async def _tag_create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # /tag create <name> <content...>
    if len(context.args) < 3:
        await update.message.reply_text(
            "Usage: <code>/tag create &lt;name&gt; &lt;content&gt;</code>",
            parse_mode="HTML",
        )
        return

    chat_id = update.effective_chat.id
    name = context.args[1].lower()
    content = " ".join(context.args[2:])

    existing = await tags.find_one({"chat_id": chat_id, "tag_name": name})
    if existing:
        await update.message.reply_text(f"A tag named <code>{escape(name)}</code> already exists!", parse_mode="HTML")
        return

    new_tag = {
        "chat_id": chat_id,
        "creator_id": update.effective_user.id,
        "tag_name": name,
        "content": content,
    }
    await tags.insert_one(new_tag)
    await update.message.reply_text(f"Tag <code>{escape(name)}</code> created successfully!", parse_mode="HTML")


async def _tag_get(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # /tag get <name>
    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: <code>/tag get &lt;name&gt;</code>",
            parse_mode="HTML",
        )
        return

    chat_id = update.effective_chat.id
    name = context.args[1].lower()

    tag_data = await tags.find_one({"chat_id": chat_id, "tag_name": name})
    if not tag_data:
        await update.message.reply_text(f"Tag <code>{escape(name)}</code> not found.", parse_mode="HTML")
        return

    await update.message.reply_text(tag_data["content"])


async def _tag_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # /tag delete <name>
    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: <code>/tag delete &lt;name&gt;</code>",
            parse_mode="HTML",
        )
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    name = context.args[1].lower()

    tag_data = await tags.find_one({"chat_id": chat_id, "tag_name": name})
    if not tag_data:
        await update.message.reply_text(f"Tag <code>{escape(name)}</code> doesn't exist.", parse_mode="HTML")
        return

    # Check permission: creator or admin
    is_creator = tag_data["creator_id"] == user_id
    is_admin = False
    if update.effective_chat.type != "private":
        member = await context.bot.get_chat_member(chat_id, user_id)
        is_admin = member.status in (ChatMember.ADMINISTRATOR, ChatMember.OWNER)

    if not is_creator and not is_admin:
        await update.message.reply_text("You didn't create this tag and you aren't an admin!")
        return

    await tags.delete_one({"_id": tag_data["_id"]})
    await update.message.reply_text(f"Tag <code>{escape(name)}</code> has been deleted.", parse_mode="HTML")


async def _tag_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    cursor = tags.find({"chat_id": chat_id})
    tag_names = [t["tag_name"] async for t in cursor]

    if not tag_names:
        await update.message.reply_text("This chat has no tags yet.")
        return

    chat_name = update.effective_chat.title or "Chat"
    tag_str = ", ".join(f"<code>{escape(n)}</code>" for n in tag_names)
    text = f"<b>{escape(chat_name)} Tags</b>\n\n{tag_str}"
    await update.message.reply_text(text, parse_mode="HTML")

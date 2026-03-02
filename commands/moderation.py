import asyncio
import logging
from collections import defaultdict, deque
from html import escape

from telegram import Update, ChatMember
from telegram.ext import ContextTypes, MessageHandler, filters
from helpers.permissions import admin_required, bot_is_admin, get_target_member_status

logger = logging.getLogger(__name__)

# Message ID tracker: {chat_id: deque([message_id, ...])}
_message_cache: dict[int, deque] = defaultdict(lambda: deque(maxlen=200))


async def track_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Passive handler that caches recent message IDs for purge support."""
    if update.effective_message and update.effective_chat:
        _message_cache[update.effective_chat.id].append(update.effective_message.message_id)


# --- /purge ---

@admin_required
async def purge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete recent messages. Usage: /purge <count>"""
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: <code>/purge &lt;count&gt;</code> (1-100)", parse_mode="HTML")
        return

    count = min(int(context.args[0]), 100)
    chat_id = update.effective_chat.id

    if not await bot_is_admin(context, chat_id):
        await update.message.reply_text("I need admin privileges to delete messages.")
        return

    cached = list(_message_cache.get(chat_id, []))
    # Include the purge command message itself
    cmd_msg_id = update.effective_message.message_id
    if cmd_msg_id not in cached:
        cached.append(cmd_msg_id)

    # Take the most recent 'count' messages (excluding the purge command which we add)
    to_delete = cached[-(count + 1):]  # +1 for the purge command itself

    deleted = 0
    for msg_id in to_delete:
        try:
            await context.bot.delete_message(chat_id, msg_id)
            deleted += 1
        except Exception:
            pass

    # Remove deleted IDs from cache
    remaining = _message_cache.get(chat_id)
    if remaining:
        for msg_id in to_delete:
            try:
                remaining.remove(msg_id)
            except ValueError:
                pass

    # Send a temporary confirmation that auto-deletes
    msg = await context.bot.send_message(chat_id, f"Deleted {deleted} messages.")
    await asyncio.sleep(3)
    try:
        await msg.delete()
    except Exception:
        pass


# --- /kick ---

@admin_required
async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kick a member. Reply to their message or: /kick <user_id|@username> [reason]"""
    chat_id = update.effective_chat.id

    if not await bot_is_admin(context, chat_id):
        await update.message.reply_text("I need admin privileges to kick members.")
        return

    target_user, reason = await _resolve_target(update, context)
    if not target_user:
        await update.message.reply_text(
            "Reply to a user's message or use: <code>/kick &lt;user_id&gt; [reason]</code>",
            parse_mode="HTML",
        )
        return

    # Check target is not admin/owner
    status = await get_target_member_status(context, chat_id, target_user.id)
    if status in (ChatMember.ADMINISTRATOR, ChatMember.OWNER):
        await update.message.reply_text("You cannot kick an admin or the group owner!")
        return

    try:
        await context.bot.ban_chat_member(chat_id, target_user.id)
        await context.bot.unban_chat_member(chat_id, target_user.id)
    except Exception as e:
        await update.message.reply_text(f"Failed to kick: {escape(str(e))}", parse_mode="HTML")
        return

    name = escape(target_user.full_name)
    mod = escape(update.effective_user.full_name)
    text = (
        f"<b>Member Kicked</b>\n\n"
        f"<b>User:</b> {name}\n"
        f"<b>Moderator:</b> {mod}\n"
        f"<b>Reason:</b> {escape(reason)}"
    )
    await update.message.reply_text(text, parse_mode="HTML")


# --- /ban ---

@admin_required
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban a member. Reply to their message or: /ban <user_id|@username> [reason]"""
    chat_id = update.effective_chat.id

    if not await bot_is_admin(context, chat_id):
        await update.message.reply_text("I need admin privileges to ban members.")
        return

    target_user, reason = await _resolve_target(update, context)
    if not target_user:
        await update.message.reply_text(
            "Reply to a user's message or use: <code>/ban &lt;user_id&gt; [reason]</code>",
            parse_mode="HTML",
        )
        return

    status = await get_target_member_status(context, chat_id, target_user.id)
    if status in (ChatMember.ADMINISTRATOR, ChatMember.OWNER):
        await update.message.reply_text("You cannot ban an admin or the group owner!")
        return

    try:
        await context.bot.ban_chat_member(chat_id, target_user.id)
    except Exception as e:
        await update.message.reply_text(f"Failed to ban: {escape(str(e))}", parse_mode="HTML")
        return

    name = escape(target_user.full_name)
    mod = escape(update.effective_user.full_name)
    text = (
        f"<b>Member Banned</b>\n\n"
        f"<b>User:</b> {name}\n"
        f"<b>Moderator:</b> {mod}\n"
        f"<b>Reason:</b> {escape(reason)}"
    )
    await update.message.reply_text(text, parse_mode="HTML")


# --- /unban ---

@admin_required
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unban a user by their numeric ID. Usage: /unban <user_id>"""
    chat_id = update.effective_chat.id

    if not await bot_is_admin(context, chat_id):
        await update.message.reply_text("I need admin privileges to unban members.")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: <code>/unban &lt;user_id&gt;</code>",
            parse_mode="HTML",
        )
        return

    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Please provide a valid numeric User ID.")
        return

    try:
        await context.bot.unban_chat_member(chat_id, user_id, only_if_banned=True)
    except Exception as e:
        await update.message.reply_text(f"Failed to unban: {escape(str(e))}", parse_mode="HTML")
        return

    try:
        user = await context.bot.get_chat(user_id)
        name = escape(user.full_name or str(user_id))
    except Exception:
        name = str(user_id)

    await update.message.reply_text(f"Unbanned <b>{name}</b>.", parse_mode="HTML")


# --- Helper ---

async def _resolve_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Resolve the target user from a reply or command args.
    Returns (User, reason) or (None, None).
    """
    reason = "No reason provided"

    # If replying to a message, the target is the author of that message
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
        if context.args:
            reason = " ".join(context.args)
        return target, reason

    # Otherwise parse args: /command <user_id> [reason...]
    if context.args:
        try:
            user_id = int(context.args[0])
            chat_member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
            target = chat_member.user
            if len(context.args) > 1:
                reason = " ".join(context.args[1:])
            return target, reason
        except (ValueError, Exception):
            pass

    return None, None


# MessageHandler for passive tracking (registered in main.py with a high group number)
message_tracker = MessageHandler(filters.ALL, track_message)

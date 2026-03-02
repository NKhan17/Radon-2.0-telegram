from functools import wraps
from telegram import ChatMember, Update
from telegram.ext import ContextTypes


def admin_required(func):
    """Decorator that checks if the calling user is a group admin or owner."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        # Allow in private chats (no admin concept)
        if update.effective_chat.type == "private":
            return await func(update, context)

        member = await context.bot.get_chat_member(chat_id, user_id)
        if member.status not in (ChatMember.ADMINISTRATOR, ChatMember.OWNER):
            await update.message.reply_text(
                "You need admin privileges for this command."
            )
            return
        return await func(update, context)
    return wrapper


async def bot_is_admin(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> bool:
    """Check if the bot itself has admin privileges in the chat."""
    bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
    return bot_member.status in (ChatMember.ADMINISTRATOR, ChatMember.OWNER)


async def get_target_member_status(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int) -> str:
    """Get a user's chat member status."""
    member = await context.bot.get_chat_member(chat_id, user_id)
    return member.status

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def paginate(items, page, per_page, callback_prefix, user_id, extra_buttons=None):
    """Build a paginated inline keyboard.

    Args:
        items: Full list of items.
        page: Current zero-indexed page number.
        per_page: Items per page.
        callback_prefix: Prefix for callback data (e.g. "diet", "mw", "flex").
        user_id: Owner user ID appended for ownership checks.
        extra_buttons: Optional list of lists of InlineKeyboardButton to append.

    Returns:
        (page_items, reply_markup, page, max_page) tuple.
    """
    max_page = max(0, (len(items) - 1) // per_page) if items else 0
    page = max(0, min(page, max_page))
    start = page * per_page
    page_items = items[start:start + per_page]

    nav_row = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton("< Prev", callback_data=f"{callback_prefix}:page:{page - 1}:{user_id}")
        )
    nav_row.append(
        InlineKeyboardButton(f"{page + 1}/{max_page + 1}", callback_data="noop")
    )
    if page < max_page:
        nav_row.append(
            InlineKeyboardButton("Next >", callback_data=f"{callback_prefix}:page:{page + 1}:{user_id}")
        )

    keyboard = [nav_row]
    if extra_buttons:
        keyboard.extend(extra_buttons)

    return page_items, InlineKeyboardMarkup(keyboard), page, max_page

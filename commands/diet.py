from html import escape
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

FOOD_DATA = [
    {"name": "Whey Protein", "protein": 80, "calories": 400},
    {"name": "Casein Protein", "protein": 75, "calories": 370},
    {"name": "Chicken Breast", "protein": 31, "calories": 165},
    {"name": "Turkey Breast", "protein": 29, "calories": 135},
    {"name": "Bison", "protein": 28, "calories": 146},
    {"name": "Tuna (Canned)", "protein": 26, "calories": 116},
    {"name": "Lean Ground Beef", "protein": 26, "calories": 250},
    {"name": "Salmon", "protein": 25, "calories": 208},
    {"name": "Seitan", "protein": 25, "calories": 141},
    {"name": "Peanut Butter", "protein": 25, "calories": 588},
    {"name": "Shrimp", "protein": 24, "calories": 99},
    {"name": "Almonds", "protein": 21, "calories": 579},
    {"name": "Cod", "protein": 20, "calories": 82},
    {"name": "Tempeh", "protein": 19, "calories": 192},
    {"name": "Chickpeas", "protein": 19, "calories": 364},
    {"name": "Whole Eggs", "protein": 13, "calories": 155},
    {"name": "Oats", "protein": 13, "calories": 389},
    {"name": "Cottage Cheese", "protein": 11, "calories": 82},
    {"name": "Edamame", "protein": 11, "calories": 122},
    {"name": "Egg Whites", "protein": 11, "calories": 52},
    {"name": "Greek Yogurt", "protein": 10, "calories": 59},
    {"name": "Tofu (Firm)", "protein": 10, "calories": 83},
    {"name": "Lentils", "protein": 9, "calories": 116},
    {"name": "Quinoa", "protein": 4, "calories": 120},
]

PER_PAGE = 10


def _sorted_data(sort_type):
    if sort_type == "protein":
        return sorted(FOOD_DATA, key=lambda x: x["protein"], reverse=True)
    return sorted(FOOD_DATA, key=lambda x: x["calories"])


def _build_diet_text(items, page, max_page, sort_type, start_index):
    if sort_type == "protein":
        title = "High Protein Rankings"
    else:
        title = "Low Calorie Rankings"

    lines = [f"<b>{title}</b>\n"]
    for i, food in enumerate(items, start_index + 1):
        name = escape(food["name"])
        if sort_type == "protein":
            lines.append(f"<b>{i}. {name}</b>\n   <b>{food['protein']}g Protein</b> | {food['calories']} kcal\n")
        else:
            lines.append(f"<b>{i}. {name}</b>\n   <b>{food['calories']} kcal</b> | {food['protein']}g protein\n")

    lines.append(f"\n<i>Page {page + 1} of {max_page + 1} | Portions per 100g</i>")
    return "\n".join(lines)


def _build_diet_keyboard(page, max_page, sort_type, user_id):
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("< Prev", callback_data=f"diet:page:{page - 1}:{sort_type}:{user_id}"))
    nav_row.append(InlineKeyboardButton(f"{page + 1}/{max_page + 1}", callback_data="noop"))
    if page < max_page:
        nav_row.append(InlineKeyboardButton("Next >", callback_data=f"diet:page:{page + 1}:{sort_type}:{user_id}"))

    sort_row = [
        InlineKeyboardButton("Sort by Protein", callback_data=f"diet:sort:protein:{user_id}"),
        InlineKeyboardButton("Sort by Calories", callback_data=f"diet:sort:calories:{user_id}"),
    ]

    return InlineKeyboardMarkup([sort_row, nav_row])


async def diet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Browse nutritional data with a food guide."""
    user_id = update.effective_user.id
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Sort by Protein", callback_data=f"diet:sort:protein:{user_id}"),
            InlineKeyboardButton("Sort by Calories", callback_data=f"diet:sort:calories:{user_id}"),
        ]
    ])

    text = (
        "<b>The Gladiator Kitchen</b>\n\n"
        "Select a sorting method to see the best fuel for your gains."
    )

    await update.message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")


async def diet_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle diet sort and pagination callbacks."""
    query = update.callback_query
    parts = query.data.split(":")
    # diet:sort:type:user_id  OR  diet:page:num:type:user_id

    if parts[0] == "noop":
        await query.answer()
        return

    action = parts[1]

    if action == "sort":
        sort_type = parts[2]
        user_id = int(parts[3])
        page = 0
    elif action == "page":
        page = int(parts[2])
        sort_type = parts[3]
        user_id = int(parts[4])
    else:
        await query.answer()
        return

    if query.from_user.id != user_id:
        await query.answer("This isn't your menu!", show_alert=True)
        return

    await query.answer()

    data = _sorted_data(sort_type)
    max_page = max(0, (len(data) - 1) // PER_PAGE)
    page = max(0, min(page, max_page))
    start = page * PER_PAGE
    page_items = data[start:start + PER_PAGE]

    text = _build_diet_text(page_items, page, max_page, sort_type, start)
    keyboard = _build_diet_keyboard(page, max_page, sort_type, user_id)

    await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")

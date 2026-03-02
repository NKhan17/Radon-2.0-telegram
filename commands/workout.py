import os
from html import escape
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.database import user_stats

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")

ROUTINES = {
    "Beginner": {
        "Gym": [("Pushups", "3x10"), ("Bicep curls", "3x10"), ("Lateral raises", "3x10"), ("Crunches", "3x10")],
        "Calisthenics": [("Push ups", "3x10"), ("Pull ups", "3x10"), ("Dips", "3x10"), ("Pike push ups", "3x10")],
    },
    "Intermediate": {
        "Gym": {
            "Monday": [("Bicep Curls", "3x10"), ("Hammer Curls", "3x10"), ("Tricep Pushdowns", "3x10"), ("Overhead Extensions", "3x10"), ("Barbell Curls", "3x10")],
            "Tuesday": [("Bicep Curls", "3x10"), ("Hammer Curls", "3x10"), ("Tricep Pushdowns", "3x10"), ("Overhead Extensions", "3x10"), ("Barbell Curls", "3x10")],
            "Wednesday": "Rest Day",
            "Thursday": [("Bench Press", "3x10"), ("Incline DB Press", "3x10"), ("Chest Flys", "3x10"), ("Leg Raises", "3x15"), ("Plank", "60s")],
            "Friday": [("Bench Press", "3x10"), ("Incline DB Press", "3x10"), ("Chest Flys", "3x10"), ("Leg Raises", "3x15"), ("Plank", "60s")],
            "Saturday": [("Back Squats", "3x10"), ("Leg Press", "3x10"), ("Calf Raises", "3x15"), ("Leg Extensions", "3x10")],
            "Sunday": "Rest Day",
        },
        "Calisthenics": {
            "Monday": [("Push ups", "3x10"), ("Inclined push ups", "3x10"), ("Dips", "3x10"), ("Pull ups (close)", "3x10"), ("Pull ups (wide)", "3x10"), ("Muscle ups", "3x10")],
            "Tuesday": [("Push ups", "3x10"), ("Inclined push ups", "3x10"), ("Dips", "3x10"), ("Pull ups (close)", "3x10"), ("Pull ups (wide)", "3x10"), ("Muscle ups", "3x10")],
            "Wednesday": "Rest Day",
            "Thursday": [("Push ups", "3x10"), ("Diamond push ups", "3x10"), ("Plank hold", "30-40s"), ("Crunches", "3x10"), ("Frog stand", "20-30s")],
            "Friday": [("Push ups", "3x10"), ("Diamond push ups", "3x10"), ("Plank hold", "30-40s"), ("Crunches", "3x10"), ("Frog stand", "20-30s")],
            "Saturday": [("Squats", "3x10"), ("Mountain climbers", "3x30"), ("Jog/run", "30 mins")],
            "Sunday": "Rest Day",
        },
    },
    "Hard": {
        "Gym": {
            "Monday": [("Bicep Curls", "4x10"), ("Hammer Curls", "4x10"), ("Tricep Pushdowns", "4x10"), ("Overhead Extensions", "4x10"), ("Barbell Curls", "4x10")],
            "Tuesday": [("Bicep Curls", "4x10"), ("Hammer Curls", "4x10"), ("Tricep Pushdowns", "4x10"), ("Overhead Extensions", "4x10"), ("Barbell Curls", "4x10")],
            "Wednesday": "Rest Day",
            "Thursday": [("Bench Press", "4x10"), ("Incline DB Press", "4x10"), ("Chest Flys", "4x10"), ("Leg Raises", "4x20"), ("Plank", "90s")],
            "Friday": [("Bench Press", "4x10"), ("Incline DB Press", "4x10"), ("Chest Flys", "4x10"), ("Leg Raises", "4x20"), ("Plank", "90s")],
            "Saturday": [("Back Squats", "4x10"), ("Leg Press", "4x10"), ("Calf Raises", "4x20"), ("Leg Extensions", "4x10")],
            "Sunday": "Rest Day",
        },
        "Calisthenics": {
            "Monday": [("Push ups", "4x10"), ("Inclined push ups", "4x10"), ("Dips", "4x10"), ("Pull ups (close)", "4x10"), ("Pull ups (wide)", "4x10"), ("Muscle ups", "4x10")],
            "Tuesday": [("Push ups", "4x10"), ("Inclined push ups", "4x10"), ("Dips", "4x10"), ("Pull ups (close)", "4x10"), ("Pull ups (wide)", "4x10"), ("Muscle ups", "4x10")],
            "Wednesday": "Rest Day",
            "Thursday": [("Push ups", "4x10"), ("Diamond push ups", "4x10"), ("Plank hold", "60s"), ("Crunches", "4x10"), ("Frog stand", "40-50s")],
            "Friday": [("Push ups", "4x10"), ("Diamond push ups", "4x10"), ("Plank hold", "60s"), ("Crunches", "4x10"), ("Frog stand", "40-50s")],
            "Saturday": [("Squats", "4x10"), ("Mountain climbers", "4x30"), ("Jog/run", "45 mins")],
            "Sunday": "Rest Day",
        },
    },
}


async def _get_user_stage(user_id):
    """Return (stage_name, workout_count) for a user."""
    user = await user_stats.find_one({"_id": user_id})
    if not user:
        return "Beginner", 0
    count = user.get("workout_count", 0)
    if count >= 30:
        return "Hard", count
    if count >= 10:
        return "Intermediate", count
    return "Beginner", count


async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display the weekly Gladiator training split."""
    text = (
        "<b>Weekly Training Split</b>\n\n"
        "Follow this routine to ensure balanced muscle recovery and maximum gains.\n\n"
        "<b>The Routine</b>\n"
        "<b>Monday:</b> Arms + Chest\n"
        "<b>Tuesday:</b> Arms + Chest\n"
        "<b>Wednesday:</b> <i>Rest &amp; Recovery</i>\n"
        "<b>Thursday:</b> Abs\n"
        "<b>Friday:</b> Abs\n"
        "<b>Saturday:</b> Leg Day\n"
        "<b>Sunday:</b> <i>Rest &amp; Recovery</i>\n\n"
        "<i>Consistency is the only shortcut. See you at the gym!</i>"
    )

    gym_path = os.path.join(ASSETS_DIR, "gym.jpg")
    if os.path.exists(gym_path):
        with open(gym_path, "rb") as photo:
            await update.message.reply_photo(photo=photo, caption=text, parse_mode="HTML")
    else:
        await update.message.reply_text(text, parse_mode="HTML")


async def startworkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start a personalized workout routine based on rank and day."""
    user_id = update.effective_user.id
    stage, count = await _get_user_stage(user_id)
    day_name = datetime.now().strftime("%A")

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Gym", callback_data=f"wo:type:gym:{user_id}"),
            InlineKeyboardButton("Calisthenics", callback_data=f"wo:type:cal:{user_id}"),
        ]
    ])

    text = (
        f"<b>Start Workout</b>\n\n"
        f"Rank: <b>{escape(stage)}</b> | Day: <b>{escape(day_name)}</b>\n\n"
        f"Choose your focus for today:"
    )

    await update.message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")


async def workout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle workout type selection and completion callbacks."""
    query = update.callback_query
    parts = query.data.split(":")
    # wo:type:{gym|cal}:user_id  OR  wo:done:user_id:old_stage

    action = parts[1]

    if action == "type":
        workout_type = parts[2]
        owner_id = int(parts[3])

        if query.from_user.id != owner_id:
            await query.answer("This isn't your workout!", show_alert=True)
            return

        await query.answer()

        path = "Gym" if workout_type == "gym" else "Calisthenics"
        stage, count = await _get_user_stage(owner_id)
        day_name = datetime.now().strftime("%A")

        stage_data = ROUTINES[stage][path]

        # Rest day check
        if isinstance(stage_data, dict):
            routine = stage_data.get(day_name, "Rest Day")
        else:
            routine = stage_data

        if routine == "Rest Day" or day_name in ("Wednesday", "Sunday"):
            text = (
                f"<b>Rest &amp; Recovery</b>\n\n"
                f"Today is <b>{escape(day_name)}</b>. Recovery is where the muscle grows. "
                f"See you tomorrow!"
            )
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=None)
            return

        # Build routine text
        lines = [f"<b>{escape(stage)} {escape(path)} Routine</b>\n"]

        if stage in ("Intermediate", "Hard"):
            lines.append("<b>Warm-up</b>\n   Stretches (5-10 mins)\n")

        for exercise, sets in routine:
            lines.append(f"<b>{escape(exercise)}</b>\n   {escape(sets)}")

        lines.append(f"\n<i>Progress: {count} workouts completed | Stay disciplined.</i>")

        text = "\n".join(lines)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Complete Workout", callback_data=f"wo:done:{owner_id}:{stage}")]
        ])

        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")

    elif action == "done":
        owner_id = int(parts[2])
        old_stage = parts[3]

        if query.from_user.id != owner_id:
            await query.answer("This isn't your workout!", show_alert=True)
            return

        await user_stats.update_one(
            {"_id": owner_id},
            {"$inc": {"workout_count": 1}},
            upsert=True,
        )

        new_stage, new_count = await _get_user_stage(owner_id)

        if new_stage != old_stage:
            msg = f"<b>LEVEL UP!</b> You've completed {new_count} workouts and reached the <b>{escape(new_stage)}</b> stage!"
        else:
            msg = f"Workout logged! ({new_count} total)"

        await query.answer(msg, show_alert=True)
        await query.edit_message_reply_markup(reply_markup=None)

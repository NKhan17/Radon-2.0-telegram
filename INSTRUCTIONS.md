# Radon 2.0 Telegram Bot - Detailed Instructions

## Table of Contents

1. [Project Overview](#project-overview)
2. [Feature Parity with Discord Bot](#feature-parity-with-discord-bot)
3. [Prerequisites](#prerequisites)
4. [Getting a Telegram Bot Token](#getting-a-telegram-bot-token)
5. [Setting Up MongoDB](#setting-up-mongodb)
6. [Local Setup](#local-setup)
7. [Configuration](#configuration)
8. [Running the Bot](#running-the-bot)
9. [Deployment](#deployment)
10. [Command Reference](#command-reference)
11. [Troubleshooting](#troubleshooting)

---

## Project Overview

Radon 2.0 Telegram Edition is a fitness-focused community bot originally built for Discord using nextcord. This version has been fully migrated to Telegram using the python-telegram-bot library while maintaining all original features.

The bot includes:
- A rank-based workout system (Beginner -> Intermediate -> Hard)
- Custom workout list management
- A nutritional food database
- Progress logging (flex log)
- Fun commands (RPS, memes, 8-ball, dad jokes)
- Group moderation tools (purge, kick, ban, unban)
- A per-chat tag system
- A workout playlist link

---

## Feature Parity with Discord Bot

| Discord Feature | Telegram Implementation | Notes |
|----------------|------------------------|-------|
| Slash commands | Bot commands (`/command`) | Identical usage |
| Embeds with colors | HTML-formatted messages | No color bars, uses bold/italic |
| Buttons | Inline keyboard buttons | Identical functionality |
| Dropdown menus | Inline keyboard button rows | Buttons instead of dropdowns |
| Modal popups (text input) | Multi-step conversation flow | Bot asks, user types, same data collected |
| Ephemeral messages | Normal replies | Telegram has no ephemeral messages in groups |
| Guild permissions | Telegram admin status checks | Admin/Owner check instead of role-based |
| `/8ball` command | `/eightball` | Telegram commands cannot start with digits |

---

## Prerequisites

- **Python 3.10+** (3.11 recommended)
- **pip** (Python package manager)
- A **Telegram account**
- A **MongoDB database** (local or cloud - MongoDB Atlas free tier works)

---

## Getting a Telegram Bot Token

1. Open Telegram and search for **@BotFather** (or go to https://t.me/BotFather)
2. Send `/start` to BotFather
3. Send `/newbot`
4. Follow the prompts:
   - Enter a **display name** for your bot (e.g., "Radon 2.0")
   - Enter a **username** for your bot (must end in "bot", e.g., "radon2_bot")
5. BotFather will give you a **token** that looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
6. **Save this token** - you'll need it for the `.env` file

### Important Bot Settings (via BotFather)

After creating your bot, send these commands to BotFather:
- `/setprivacy` -> Select your bot -> **Disable** (so the bot can see all messages for the purge tracker)
- `/setjoingroups` -> Select your bot -> **Enable** (so it can be added to groups)

---

## Setting Up MongoDB

### Option A: MongoDB Atlas (Cloud - Recommended)

1. Go to https://www.mongodb.com/atlas and create a free account
2. Create a **free shared cluster**
3. Under **Database Access**, create a database user with a password
4. Under **Network Access**, add your IP (or `0.0.0.0/0` to allow all)
5. Click **Connect** on your cluster -> **Drivers** -> Copy the connection string
6. It will look like: `mongodb+srv://username:password@cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority`
7. Replace `<password>` with your actual database user password

### Option B: Local MongoDB

1. Install MongoDB Community Edition: https://www.mongodb.com/try/download/community
2. Start the MongoDB service
3. Your connection string will be: `mongodb://localhost:27017`

---

## Local Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/NKhan17/Radon-2.0-telegram.git
cd Radon-2.0-telegram
```

### Step 2: Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy the example env file
cp .env.example .env    # macOS/Linux
copy .env.example .env  # Windows
```

Edit the `.env` file with your values:

```env
BOT_TOKEN=your_telegram_bot_token_here
MONGO_URI=your_mongodb_connection_string_here
```

---

## Configuration

The bot uses two environment variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | Yes | Your Telegram bot token from @BotFather |
| `MONGO_URI` | Yes | MongoDB connection string |

The bot validates these on startup and will exit with a clear message if any are missing.

---

## Running the Bot

```bash
python main.py
```

You should see:
```
INFO - Bot commands registered with Telegram.
INFO - Radon 2.0 Telegram Edition is online!
INFO - Starting Radon 2.0 polling...
```

### Adding the Bot to a Group

1. Open your bot's chat in Telegram (search for its @username)
2. Send `/start` to verify it works
3. Add it to a group
4. **Make the bot an admin** in the group (required for moderation commands and message tracking)

---

## Deployment

### Docker

```bash
# Build
docker build -t radon-telegram .

# Run
docker run -d --env-file .env --name radon-bot radon-telegram
```

### Railway

1. Fork/push this repo to your GitHub
2. Go to https://railway.app and create a new project
3. Select "Deploy from GitHub repo"
4. Add environment variables (`BOT_TOKEN`, `MONGO_URI`) in the Variables tab
5. Railway will auto-detect the Dockerfile and deploy

### Render

1. Go to https://render.com and create a new **Background Worker**
2. Connect your GitHub repo
3. Set:
   - **Runtime:** Docker
   - **Environment Variables:** `BOT_TOKEN`, `MONGO_URI`
4. Deploy

### VPS (Ubuntu/Debian)

```bash
# Install Python
sudo apt update && sudo apt install python3 python3-pip python3-venv -y

# Clone and setup
git clone https://github.com/NKhan17/Radon-2.0-telegram.git
cd Radon-2.0-telegram
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Add your secrets

# Run with systemd (persistent)
sudo tee /etc/systemd/system/radon-bot.service > /dev/null <<EOF
[Unit]
Description=Radon 2.0 Telegram Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/python main.py
Restart=always
RestartSec=10
EnvironmentFile=$(pwd)/.env

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable radon-bot
sudo systemctl start radon-bot
sudo systemctl status radon-bot
```

### Heroku

The included `Procfile` supports Heroku deployment:

```bash
heroku create your-bot-name
heroku config:set BOT_TOKEN=your_token MONGO_URI=your_uri
git push heroku main
heroku ps:scale worker=1
```

---

## Command Reference

### Workout Commands

**`/schedule`**
View the weekly training split.
```
/schedule
```

**`/startworkout`**
Start your personalized workout based on your rank and the current day.
```
/startworkout
```
Then select "Gym" or "Calisthenics" from the buttons. After completing the routine, press "Complete Workout" to log it.

**Rank System:**
- Beginner: 0-9 completed workouts
- Intermediate: 10-29 completed workouts
- Hard: 30+ completed workouts

**`/myworkout`**
View and manage your custom exercise list.
```
/myworkout
```
Use the inline buttons to Add, Delete, or Clear exercises. Navigate pages with Prev/Next.

### Nutrition

**`/diet`**
Browse the nutritional food database.
```
/diet
```
Sort by protein or calories using the buttons. Navigate with Prev/Next.

### Progress

**`/flex`**
View and manage your progress log.
```
/flex
```
Use Add to log a new achievement, Delete to remove entries, Clear All to reset.

### Fun Commands

**`/rps`**
Play Rock Paper Scissors against Radon.
```
/rps
```

**`/meme`**
Get a random meme.
```
/meme
```

**`/eightball`**
Ask the magic 8-ball a question.
```
/eightball Will I ever bench 225?
```

**`/dadjoke`**
Get a random dad joke.
```
/dadjoke
```

**`/hype`**
Get the official Radon workout playlist.
```
/hype
```

### Tags

**`/tag create <name> <content>`**
Create a new tag for this chat.
```
/tag create rules No skipping leg day!
```

**`/tag get <name>`**
View a tag's content.
```
/tag get rules
```

**`/tag delete <name>`**
Delete a tag (creator or admin only).
```
/tag delete rules
```

**`/tag list`**
List all tags in this chat.
```
/tag list
```

### Moderation (Admin Only)

**`/purge <count>`**
Delete recent messages (up to 100, max 48h old).
```
/purge 10
```

**`/kick`**
Kick a user. Reply to their message or provide a user ID.
```
/kick               (reply to a message)
/kick 123456789     (by user ID)
/kick 123456789 Spamming
```

**`/ban`**
Ban a user. Reply to their message or provide a user ID.
```
/ban                (reply to a message)
/ban 123456789 Toxic behavior
```

**`/unban <user_id>`**
Unban a user by their numeric Telegram ID.
```
/unban 123456789
```

---

## Troubleshooting

### Bot doesn't respond to commands
- Make sure `BOT_TOKEN` is correct in `.env`
- Check that the bot is running (`python main.py` should show "online" message)
- In groups, make sure you're using the command with the bot's username: `/command@yourbotname`

### Bot can't kick/ban/purge
- The bot must be an **admin** in the group
- For purge: BotFather privacy mode must be **disabled** (`/setprivacy` -> Disable)
- Purge only works for messages sent after the bot joined (it tracks message IDs passively)
- Messages older than 48 hours cannot be deleted (Telegram API limitation)

### MongoDB connection errors
- Check your `MONGO_URI` is correct
- If using Atlas: make sure your IP is in the Network Access whitelist
- If using Atlas: make sure the database user password is correct (no special characters that need URL encoding)

### "Missing required environment variables" error
- Copy `.env.example` to `.env`: `cp .env.example .env`
- Fill in both `BOT_TOKEN` and `MONGO_URI`

### Multi-step inputs (Add/Delete) not working
- Type `/cancel` to exit any stuck conversation
- Make sure you're replying with plain text (not commands) when the bot asks for input

### Bot works in private chat but not in groups
- Add the bot to the group
- Make the bot an admin
- Disable privacy mode via BotFather (`/setprivacy`)

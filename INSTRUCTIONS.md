# Radon 2.0 Telegram Bot - Detailed Instructions

## Table of Contents

1. [Project Overview](#project-overview)
2. [Feature Parity with Discord Bot](#feature-parity-with-discord-bot)
3. [Prerequisites](#prerequisites)
4. [Getting a Telegram Bot Token](#getting-a-telegram-bot-token)
5. [Setting Up MongoDB](#setting-up-mongodb)
6. [Deploy to Vercel (Recommended)](#deploy-to-vercel-recommended)
7. [Run Locally (Polling Mode)](#run-locally-polling-mode)
8. [Other Deployment Options](#other-deployment-options)
9. [Command Reference](#command-reference)
10. [Troubleshooting](#troubleshooting)

---

## Project Overview

Radon 2.0 Telegram Edition is a fitness-focused community bot originally built for Discord using nextcord. This version has been fully migrated to Telegram using the python-telegram-bot library while maintaining all original features.

The bot supports **two deployment modes**:
- **Vercel (webhook mode)** - Serverless, zero infrastructure, always on. Telegram pushes updates to your Vercel function.
- **Local/VPS (polling mode)** - Traditional long-running process that polls Telegram for updates.

The bot includes:
- A rank-based workout system (Beginner -> Intermediate -> Hard)
- Custom workout list management
- A nutritional food database
- Progress logging (flex log)
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

- A **Telegram account**
- A **MongoDB database** (MongoDB Atlas free tier works)
- For Vercel: A **GitHub account** and **Vercel account** (both free)
- For local: **Python 3.10+** and **pip**

---

## Getting a Telegram Bot Token

1. Open Telegram and search for **@BotFather** (or go to https://t.me/BotFather)
2. Send `/start` to BotFather
3. Send `/newbot`
4. Follow the prompts:
   - Enter a **display name** for your bot (e.g., "Radon 2.0")
   - Enter a **username** for your bot (must end in "bot", e.g., "radon2_bot")
5. BotFather will give you a **token** that looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
6. **Save this token** - you'll need it for deployment

### Important Bot Settings (via BotFather)

After creating your bot, send these commands to BotFather:
- `/setprivacy` -> Select your bot -> **Disable** (so the bot can see all messages for the purge tracker)
- `/setjoingroups` -> Select your bot -> **Enable** (so it can be added to groups)

---

## Setting Up MongoDB

### MongoDB Atlas (Cloud - Recommended)

1. Go to https://www.mongodb.com/atlas and create a free account
2. Create a **free shared cluster** (M0 tier is free forever)
3. Under **Database Access**, create a database user with a password
4. Under **Network Access**, add `0.0.0.0/0` (allow access from anywhere - needed for Vercel)
5. Click **Connect** on your cluster -> **Drivers** -> Copy the connection string
6. It will look like: `mongodb+srv://username:password@cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority`
7. Replace `<password>` with your actual database user password

**Important for Vercel:** You must allow access from all IPs (`0.0.0.0/0`) because Vercel serverless functions use dynamic IPs.

---

## Deploy to Vercel (Recommended)

This is the easiest way to get the bot running 24/7 with zero infrastructure costs.

### How it Works

Unlike the local polling mode where the bot continuously asks Telegram "any new messages?", Vercel uses **webhooks**: Telegram sends a POST request to your Vercel URL whenever someone sends a message. Your serverless function wakes up, processes the message, and goes back to sleep. This means:

- No server to maintain
- No process to keep alive
- Free tier handles thousands of messages/day
- Automatic HTTPS (required by Telegram)
- ConversationHandler state is persisted to MongoDB (survives cold starts)

### Step-by-Step

#### 1. Fork the Repository

Go to https://github.com/NKhan17/Radon-2.0-telegram and click **Fork** (top right).

#### 2. Create a Vercel Account

Go to https://vercel.com and sign up with your GitHub account (free).

#### 3. Import the Project

1. In Vercel dashboard, click **"Add New..." -> "Project"**
2. Select your forked repository
3. Vercel will auto-detect the `vercel.json` configuration
4. **Before clicking Deploy**, add your environment variables (see next step)

> **"Project already exists" error:** Vercel project names are **globally unique**
> across all Vercel users. If the default name (e.g. `radon-2-0-telegram`) is
> already taken by someone else, Vercel will show this error even though it's
> your first time deploying. To fix this:
>
> - In the import screen, look for the **"Project Name"** field
> - Change it to something unique, e.g. `radon-bot-yourname` or `radon-tg-12345`
> - The project name only affects your Vercel dashboard URL � it does **not**
>   affect bot functionality

#### 4. Add Environment Variables

In the Vercel project settings (or during import), add:

| Key | Value |
|-----|-------|
| `BOT_TOKEN` | Your bot token from @BotFather |
| `MONGO_URI` | Your MongoDB Atlas connection string |

Click **Deploy**.

#### 5. Register the Webhook

After deployment completes, Vercel gives you a URL like `https://your-project.vercel.app`.

**Open this URL in your browser:**

```
https://your-project.vercel.app/api/set_webhook
```

You should see a JSON response like:
```json
{
  "ok": true,
  "webhook_url": "https://your-project.vercel.app/api/webhook",
  "pending_update_count": 0
}
```

This tells Telegram to send all bot updates to your Vercel function.

#### 6. Test the Bot

Open Telegram, find your bot, and send `/start`. It should respond.

#### 7. Verify Everything

You can check webhook status anytime:
```
https://your-project.vercel.app/api/set_webhook?action=info
```

### Webhook Management

| URL | Action |
|-----|--------|
| `/api/set_webhook` | Register/update the webhook |
| `/api/set_webhook?action=info` | Check current webhook status |
| `/api/set_webhook?action=delete` | Remove webhook (for switching to polling mode) |
| `/api/webhook` | The actual webhook endpoint (Telegram POSTs here) |

### Using a Custom Domain

If you add a custom domain in Vercel, set the `WEBHOOK_URL` environment variable:

```
WEBHOOK_URL=https://your-custom-domain.com
```

Then visit `/api/set_webhook` again to re-register with the new URL.

### Updating the Bot

Push changes to your GitHub repo. Vercel auto-deploys on every push. The webhook URL stays the same.

---

## Run Locally (Polling Mode)

For development or self-hosted deployment.

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

Edit the `.env` file:

```env
BOT_TOKEN=your_telegram_bot_token_here
MONGO_URI=your_mongodb_connection_string_here
```

### Step 5: Remove Webhook (if previously set)

If you previously deployed on Vercel, delete the webhook first so polling mode works:

```bash
curl "https://api.telegram.org/botYOUR_TOKEN/deleteWebhook"
```

### Step 6: Run

```bash
python main.py
```

You should see:
```
INFO - Bot commands registered with Telegram.
INFO - Radon 2.0 Telegram Edition is online! (polling mode)
INFO - Starting Radon 2.0 polling...
```

### Adding the Bot to a Group

1. Open your bot's chat in Telegram (search for its @username)
2. Send `/start` to verify it works
3. Add it to a group
4. **Make the bot an admin** in the group (required for moderation commands and message tracking)

---

## Other Deployment Options

### Docker

```bash
docker build -t radon-telegram .
docker run -d --env-file .env --name radon-bot radon-telegram
```

### Railway

1. Fork the repo to your GitHub
2. Go to https://railway.app and create a new project
3. Select "Deploy from GitHub repo"
4. Add environment variables (`BOT_TOKEN`, `MONGO_URI`) in the Variables tab
5. Railway auto-detects the Dockerfile

### Render

1. Go to https://render.com and create a new **Background Worker**
2. Connect your GitHub repo
3. Set Runtime to Docker, add `BOT_TOKEN` and `MONGO_URI` as env vars

### VPS (Ubuntu/Debian)

```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv -y

git clone https://github.com/NKhan17/Radon-2.0-telegram.git
cd Radon-2.0-telegram
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env  # Add your secrets

# Run as a systemd service for persistence:
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
```

### Heroku

```bash
heroku create your-bot-name
heroku config:set BOT_TOKEN=your_token MONGO_URI=your_uri
git push heroku main
heroku ps:scale worker=1
```

---

## Command Reference

### Workout Commands

**`/schedule`** - View the weekly training split.
```
/schedule
```

**`/startworkout`** - Start your personalized workout based on your rank and the current day.
```
/startworkout
```
Then select "Gym" or "Calisthenics" from the buttons. After completing the routine, press "Complete Workout" to log it.

**Rank System:**
- Beginner: 0-9 completed workouts
- Intermediate: 10-29 completed workouts
- Hard: 30+ completed workouts

**`/myworkout`** - View and manage your custom exercise list.
```
/myworkout
```
Use the inline buttons to Add, Delete, or Clear exercises.

### Nutrition

**`/diet`** - Browse the nutritional food database.
```
/diet
```
Sort by protein or calories using the buttons. Navigate pages with Prev/Next.

### Progress

**`/flex`** - View and manage your progress log.
```
/flex
```
Use Add to log a new achievement, Delete to remove entries, Clear All to reset.

### Fun Commands

```
/rps          - Rock Paper Scissors
/eightball    - Magic 8-ball (add your question after the command)
/dadjoke      - Dad joke
/hype         - Workout playlist link
```

### Tags

```
/tag create <name> <content>  - Create a tag
/tag get <name>               - View a tag
/tag delete <name>            - Delete a tag (creator/admin)
/tag list                     - List all tags
```

### Moderation (Admin Only)

```
/purge <count>    - Delete recent messages (1-100)
/kick             - Kick (reply to message or: /kick <user_id> [reason])
/ban              - Ban  (reply to message or: /ban <user_id> [reason])
/unban <user_id>  - Unban by numeric user ID
```

---

## Troubleshooting

### Bot doesn't respond to commands
- **Vercel:** Check that the webhook is registered (visit `/api/set_webhook?action=info`)
- **Local:** Check that `python main.py` is running and showing "online"
- Make sure `BOT_TOKEN` is correct
- In groups, try `/command@yourbotname`

### Vercel: Bot responds slowly on first message
This is a **cold start** - the serverless function hasn't been called recently. First response may take 1-3 seconds. Subsequent responses are fast (~100-200ms).

### Vercel: ConversationHandler state lost
If mid-conversation state (like adding an exercise) seems lost, the MongoDB persistence should handle this automatically. Check that `MONGO_URI` is valid and the `GymBotDB.bot_persistence` collection is accessible.

### Vercel: Webhook registration fails
- Check that `BOT_TOKEN` is set in Vercel environment variables
- Make sure there are no typos in the token
- Try visiting `/api/set_webhook?action=delete` first, then `/api/set_webhook` again

### Bot can't kick/ban/purge
- The bot must be an **admin** in the group
- For purge: BotFather privacy mode must be **disabled** (`/setprivacy` -> Disable)
- Purge only works for messages sent after the bot joined (it tracks message IDs passively)
- Messages older than 48 hours cannot be deleted (Telegram API limitation)

### MongoDB connection errors
- Check your `MONGO_URI` is correct
- If using Atlas: make sure Network Access allows `0.0.0.0/0` (required for Vercel)
- Make sure the database user password has no special characters that need URL encoding

### "Missing required environment variables" error
- **Vercel:** Add `BOT_TOKEN` and `MONGO_URI` in project Settings -> Environment Variables, then redeploy
- **Local:** Copy `.env.example` to `.env` and fill in the values

### Multi-step inputs (Add/Delete) not working
- Type `/cancel` to exit any stuck conversation
- Make sure you're replying with plain text (not commands) when the bot asks for input

### Switching between Vercel and local mode
- **To use local after Vercel:** Delete the webhook first: visit `/api/set_webhook?action=delete` or run `curl "https://api.telegram.org/botYOUR_TOKEN/deleteWebhook"`
- **To use Vercel after local:** Stop the local process and register the webhook: visit `/api/set_webhook`
- You cannot run both modes simultaneously for the same bot token.

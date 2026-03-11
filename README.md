# Radon 2.0 - Telegram Edition

A full-featured Telegram bot migrated from the [Radon 2.0 Discord bot](https://github.com/realquazar/Radon-2.0). This bot is a fitness-focused community companion with workout tracking, nutrition guides, progress logging, fun commands, moderation tools, and a tag system.

## Features

- **Workout System** - Level-based training routines (Beginner/Intermediate/Hard) with Gym and Calisthenics options
- **Custom Workouts** - Create and manage your personal exercise list
- **Nutrition Guide** - Browse 24 foods sorted by protein or calories
- **Progress Tracking** - Log and view your fitness milestones
- **Fun Commands** - Rock Paper Scissors, 8-ball, dad jokes
- **Moderation** - Purge, kick, ban, unban with admin checks
- **Tags** - Per-chat tag system for saving and sharing content
- **Workout Playlist** - Official hype playlist link

## Deploy to Render (Free Tier)

Render's **Web Service** (free tier) is used. `server.py` runs the polling bot in a background thread alongside a tiny HTTP health-check server — this satisfies Render's port-binding requirement for free web services.

1. Fork this repo to your GitHub account
2. Go to [render.com](https://render.com) → **New** → **Web Service**
3. Connect your GitHub repo
4. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python server.py`
5. Add environment variables in the Render dashboard:
   - `BOT_TOKEN` — your Telegram bot token from [@BotFather](https://t.me/BotFather)
   - `MONGO_URI` — your MongoDB connection string (e.g. from [MongoDB Atlas](https://www.mongodb.com/atlas))
6. Click **Create Web Service** — check the logs for `Radon 2.0 Telegram Edition is online!`
7. Send `/start` to your bot in Telegram to confirm it's live

> **Free tier spin-down:** Render's free Web Services sleep after ~15 minutes of no HTTP traffic. To prevent this, add your Render URL to [UptimeRobot](https://uptimerobot.com) (free) with a 5-minute ping interval. This keeps the bot alive 24/7 at no cost.

## Run Locally (Polling Mode)

```bash
cp .env.example .env   # Fill in BOT_TOKEN and MONGO_URI
pip install -r requirements.txt
python main.py
```

## Required Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | Yes | Telegram bot token from [@BotFather](https://t.me/BotFather) |
| `MONGO_URI` | Yes | MongoDB connection string |

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot |
| `/help` | Show all commands |
| `/schedule` | View weekly training split |
| `/startworkout` | Start your level-based workout |
| `/myworkout` | View/edit custom workout list |
| `/diet` | Browse nutritional food guide |
| `/flex` | View/edit progress log |
| `/rps` | Rock Paper Scissors |
| `/eightball` | Magic 8-ball |
| `/dadjoke` | Dad joke |
| `/hype` | Workout playlist |
| `/tag` | Manage chat tags |
| `/purge` | Delete messages (admin) |
| `/kick` | Kick user (admin) |
| `/ban` | Ban user (admin) |
| `/unban` | Unban user (admin) |

## Architecture

The bot runs in **polling mode** via `server.py`:
- A daemon thread runs `main.py`'s polling loop (0.5s interval) continuously
- The main thread runs a lightweight `aiohttp` health-check server on `$PORT`
- Render sees an active HTTP server and keeps the process alive on the free tier
- UptimeRobot pings `/health` every 5 minutes to prevent free-tier spin-down

## Tech Stack

- Python 3.10+
- python-telegram-bot v20+
- MongoDB (motor async driver)
- aiohttp

## Project Structure

```
├── server.py             # Render entry point (bot thread + health-check server)
├── main.py               # Local polling entry point
├── bot_app.py            # Shared Application builder
├── Procfile              # Render process declaration (web: python server.py)
├── Dockerfile            # Docker deployment config
├── config/settings.py    # Env var loading + validation
├── services/
│   ├── database.py       # MongoDB connection
│   ├── api_client.py     # External API helpers
│   └── persistence.py    # MongoDB persistence for ConversationHandlers
├── commands/             # All command modules
├── helpers/              # Shared utilities
└── assets/               # Images
```

## License

MIT

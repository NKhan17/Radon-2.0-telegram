# Radon 2.0 - Telegram Edition

A full-featured Telegram bot migrated from the [Radon 2.0 Discord bot](https://github.com/realquazar/Radon-2.0). This bot is a fitness-focused community companion with workout tracking, nutrition guides, progress logging, fun commands, moderation tools, and a tag system.

## Features

- **Workout System** - Level-based training routines (Beginner/Intermediate/Hard) with Gym and Calisthenics options
- **Custom Workouts** - Create and manage your personal exercise list
- **Nutrition Guide** - Browse 24 foods sorted by protein or calories
- **Progress Tracking** - Log and view your fitness milestones
- **Fun Commands** - Rock Paper Scissors, memes, 8-ball, dad jokes
- **Moderation** - Purge, kick, ban, unban with admin checks
- **Tags** - Per-chat tag system for saving and sharing content
- **Workout Playlist** - Official hype playlist link

## Deploy to Vercel (Recommended)

The fastest way to get the bot running with zero infrastructure:

1. Fork this repo to your GitHub account
2. Go to [vercel.com](https://vercel.com) and import the repo
3. Add environment variables in Vercel dashboard:
   - `BOT_TOKEN` - your Telegram bot token from [@BotFather](https://t.me/BotFather)
   - `MONGO_URI` - your MongoDB connection string
4. Deploy (Vercel auto-detects the config)
5. Register the webhook: visit `https://your-project.vercel.app/api/set_webhook`
6. Send `/start` to your bot in Telegram

See [INSTRUCTIONS.md](INSTRUCTIONS.md) for the full walkthrough.

## Run Locally (Polling Mode)

```bash
cp .env.example .env   # Fill in BOT_TOKEN and MONGO_URI
pip install -r requirements.txt
python main.py
```

## Required Secrets

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | Yes | Telegram bot token from [@BotFather](https://t.me/BotFather) |
| `MONGO_URI` | Yes | MongoDB connection string |
| `WEBHOOK_URL` | No | Custom domain for Vercel (auto-detected if not set) |

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
| `/meme` | Random meme |
| `/eightball` | Magic 8-ball |
| `/dadjoke` | Dad joke |
| `/hype` | Workout playlist |
| `/tag` | Manage chat tags |
| `/purge` | Delete messages (admin) |
| `/kick` | Kick user (admin) |
| `/ban` | Ban user (admin) |
| `/unban` | Unban user (admin) |

## Architecture

The bot supports two deployment modes:

- **Vercel (webhook)** - Telegram pushes updates to `/api/webhook`. Serverless, zero infrastructure, always on. ConversationHandler state persisted to MongoDB.
- **Local/VPS (polling)** - `main.py` polls Telegram for updates. Traditional long-running process.

## Tech Stack

- Python 3.10+
- python-telegram-bot v20+
- MongoDB (motor async driver)
- aiohttp

## Project Structure

```
├── main.py               # Polling mode entry point
├── bot_app.py            # Shared Application builder (both modes)
├── vercel.json           # Vercel deployment config
├── api/
│   ├── webhook.py        # Vercel webhook handler (serverless)
│   └── set_webhook.py    # Webhook registration helper
├── config/settings.py    # Env var loading + validation
├── services/
│   ├── database.py       # MongoDB connection
│   ├── api_client.py     # External API helpers
│   └── persistence.py    # MongoDB persistence for serverless
├── commands/             # All command modules
├── helpers/              # Shared utilities
└── assets/               # Images
```

## License

MIT

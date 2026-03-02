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

## Quick Start

1. Copy `.env.example` to `.env` and fill in your secrets
2. `pip install -r requirements.txt`
3. `python main.py`

See [INSTRUCTIONS.md](INSTRUCTIONS.md) for detailed setup and deployment guide.

## Required Secrets

| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Telegram bot token from [@BotFather](https://t.me/BotFather) |
| `MONGO_URI` | MongoDB connection string |

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

## Tech Stack

- Python 3.11+
- python-telegram-bot v20+
- MongoDB (motor async driver)
- aiohttp

## Project Structure

```
telegram-bot/
  main.py               # Entry point
  config/settings.py    # Env var loading
  services/database.py  # MongoDB connection
  services/api_client.py # External API helpers
  commands/             # All command modules
  helpers/              # Shared utilities
  assets/               # Images
```

## License

MIT

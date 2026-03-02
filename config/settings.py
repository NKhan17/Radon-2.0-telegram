import os
import sys
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

REQUIRED_VARS = {
    "BOT_TOKEN": BOT_TOKEN,
    "MONGO_URI": MONGO_URI,
}


def validate_env():
    """Validate that all required environment variables are set."""
    missing = [name for name, value in REQUIRED_VARS.items() if not value]
    if missing:
        print(f"Missing required environment variables: {', '.join(missing)}")
        print("Please copy .env.example to .env and fill in the values.")
        sys.exit(1)

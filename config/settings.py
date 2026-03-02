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
    """Validate that all required environment variables are set.

    In polling mode (main.py), exits the process on failure.
    In serverless mode (Vercel), raises RuntimeError instead of killing
    the process at module-load time.
    """
    missing = [name for name, value in REQUIRED_VARS.items() if not value]
    if missing:
        msg = f"Missing required environment variables: {', '.join(missing)}"
        if os.getenv("VERCEL"):
            raise RuntimeError(msg)
        print(msg)
        print("Please copy .env.example to .env and fill in the values.")
        sys.exit(1)

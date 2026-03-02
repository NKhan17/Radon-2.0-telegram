import motor.motor_asyncio
from config.settings import MONGO_URI

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)

# GymBotDB collections
gym_db = client["GymBotDB"]
user_stats = gym_db["user_stats"]
custom_workouts = gym_db["custom_workouts"]
user_flexes = gym_db["user_flexes"]

# RadonDB collections
radon_db = client["RadonDB"]
tags = radon_db["tags"]

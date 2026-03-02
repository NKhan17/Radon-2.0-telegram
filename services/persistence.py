"""MongoDB-backed persistence for python-telegram-bot.

Stores ConversationHandler state and user_data in MongoDB so that
serverless deployments (Vercel, AWS Lambda, etc.) survive cold starts.
"""

import asyncio
from copy import deepcopy
from typing import Any, Dict, Optional, Tuple

from telegram.ext import BasePersistence, PersistenceInput
from telegram.ext._utils.types import ConversationDict, CDCData

from services.database import gym_db


class MongoPersistence(BasePersistence):
    """Persist conversation and user data to MongoDB."""

    def __init__(self):
        super().__init__(
            store_data=PersistenceInput(
                bot_data=False,
                chat_data=False,
                user_data=True,
                callback_data=False,
            ),
        )
        self._collection = gym_db["bot_persistence"]
        self._conversations: Dict[str, ConversationDict] = {}
        self._user_data: Dict[int, Dict] = {}

    # --- Load methods (called once at startup) ---

    async def get_bot_data(self) -> Dict:
        return {}

    async def get_chat_data(self) -> Dict[int, Dict]:
        return {}

    async def get_user_data(self) -> Dict[int, Dict]:
        doc = await self._collection.find_one({"_id": "user_data"})
        if doc and "data" in doc:
            # MongoDB doesn't allow integer keys, so they're stored as strings
            self._user_data = {int(k): v for k, v in doc["data"].items()}
        return deepcopy(self._user_data)

    async def get_callback_data(self) -> Optional[CDCData]:
        return None

    async def get_conversations(self, name: str) -> ConversationDict:
        doc = await self._collection.find_one({"_id": f"conv:{name}"})
        if doc and "data" in doc:
            # Keys are stored as strings, convert back to tuples
            conv = {}
            for key_str, state in doc["data"].items():
                parts = key_str.split(",")
                if len(parts) == 2:
                    key = (int(parts[0]), int(parts[1]))
                else:
                    key = (int(parts[0]),)
                conv[key] = state
            self._conversations[name] = conv
        else:
            self._conversations[name] = {}
        return deepcopy(self._conversations.get(name, {}))

    # --- Update methods (called after each update is processed) ---

    async def update_bot_data(self, data: Dict) -> None:
        pass

    async def update_chat_data(self, chat_id: int, data: Dict) -> None:
        pass

    async def update_user_data(self, user_id: int, data: Dict) -> None:
        self._user_data[user_id] = data
        serializable = {str(k): v for k, v in self._user_data.items()}
        await self._collection.update_one(
            {"_id": "user_data"},
            {"$set": {"data": serializable}},
            upsert=True,
        )

    async def update_callback_data(self, data: CDCData) -> None:
        pass

    async def update_conversation(
        self, name: str, key: Tuple[int, ...], new_state: Optional[object]
    ) -> None:
        if name not in self._conversations:
            self._conversations[name] = {}

        if new_state is None:
            self._conversations[name].pop(key, None)
        else:
            self._conversations[name][key] = new_state

        # Serialize tuple keys to comma-separated strings
        serializable = {
            ",".join(str(p) for p in k): v
            for k, v in self._conversations[name].items()
        }
        await self._collection.update_one(
            {"_id": f"conv:{name}"},
            {"$set": {"data": serializable}},
            upsert=True,
        )

    async def drop_chat_data(self, chat_id: int) -> None:
        pass

    async def drop_user_data(self, user_id: int) -> None:
        self._user_data.pop(user_id, None)

    async def flush(self) -> None:
        pass

    async def refresh_bot_data(self, bot_data: Dict) -> None:
        pass

    async def refresh_chat_data(self, chat_id: int, chat_data: Dict) -> None:
        pass

    async def refresh_user_data(self, user_id: int, user_data: Dict) -> None:
        pass

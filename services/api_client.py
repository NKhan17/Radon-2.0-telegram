import aiohttp


async def fetch_meme():
    """Fetch a random meme from meme-api.com."""
    async with aiohttp.ClientSession() as session:
        async with session.get("https://meme-api.com/gimme") as resp:
            if resp.status != 200:
                return None
            return await resp.json()


async def fetch_dad_joke():
    """Fetch a random dad joke from icanhazdadjoke.com."""
    async with aiohttp.ClientSession() as session:
        headers = {"Accept": "application/json"}
        async with session.get("https://icanhazdadjoke.com/", headers=headers) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            return data.get("joke")

import aiohttp




async def fetch_dad_joke():
    """Fetch a random dad joke from icanhazdadjoke.com."""
    async with aiohttp.ClientSession() as session:
        headers = {"Accept": "application/json"}
        async with session.get("https://icanhazdadjoke.com/", headers=headers) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            return data.get("joke")

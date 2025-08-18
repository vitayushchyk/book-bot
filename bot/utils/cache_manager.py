import json

from bot.db.conection import redis


class CacheManager:
    def __init__(self):
        self.redis_client = redis

    async def get_cached_books(self, query: str):
        cached_data = await self.redis_client.get(query)
        return None if not cached_data else json.loads(cached_data)

    async def set_cached_books(self, query: str, data: list, ttl: int = 86400):
        await self.redis_client.setex(query, ttl, json.dumps(data))

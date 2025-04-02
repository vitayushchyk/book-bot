import json

import redis

from bot.core.config import settings


class CacheManager:
    def __init__(self):

        self.redis_client = redis.StrictRedis(
            host=settings.redis_host, port=settings.redis_port, decode_responses=True
        )

    def get_cached_books(self, query: str):

        cached_data = self.redis_client.get(query)
        return None if not cached_data else json.loads(cached_data)

    def set_cached_books(self, query: str, data: list, ttl: int = 86400):
        self.redis_client.setex(query, ttl, json.dumps(data))

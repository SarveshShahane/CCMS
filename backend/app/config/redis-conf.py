import redis.asyncio as redis
from app.config.env import settings


class RedisConfig:
    def __init__(self):
        self.host: str = settings.redis_host
        self.port: int = settings.redis_port
        self.url: str = settings.redis_url
        self.pool: redis.ConnectionPool = redis.ConnectionPool.from_url(self.url)

    def get_client(self) -> redis.Redis:
        return redis.Redis(connection_pool=self.pool)


redis_config = RedisConfig()
redis_client: redis.Redis = redis_config.get_client()


async def get_redis():
    client = redis.Redis(connection_pool=redis_config.pool)
    try:
        yield client
    finally:
        await client.close()
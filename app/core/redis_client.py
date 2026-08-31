from aredis_om import get_redis_connection

from .config import get_settings


settings = get_settings()


redis_client = get_redis_connection(
    url=settings.redis_url,
    decode_responses=True,
)

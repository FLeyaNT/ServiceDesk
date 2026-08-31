from aredis_om import HashModel, Field

from datetime import datetime

from core.redis_client import redis_client
from core.config import get_settings


settings = get_settings()


class Session(HashModel, index=True):
    user_id: int = Field(index=True)
    username: str
    full_name: str
    role: str
    created_at: datetime
    expires_in: int
    last_activity: datetime
    ip_address: str | None = None
    user_agent: str | None = None

    class Meta:
        database = redis_client
        global_key_prefix = settings.app_name
        model_key_prefix = 'session'

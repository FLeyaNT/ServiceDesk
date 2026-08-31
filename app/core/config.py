from pydantic_settings import BaseSettings

from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = 'Service Desk API'
    version: str = '1.0.0'
    description: str = 'API для информационной системы технической поддержки'
    debug: bool = True

    # ========== PostgreSQL ==========

    postgres_user: str = 'postgres'
    postgres_password: str = 'postgres'
    postgres_host: str = 'localhost'
    postgres_port: int = 5432
    postgres_db: str = 'service_desk_system'

    # ========== Redis ==========

    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    # ========== Sessions ==========

    session_ttl: int = 60 * 60 * 2
    session_cookie_name: str = 'session_id'
    cookie_secret_key: str = 'sdhsdhdsh-sashbash-ioresngvjwhklnakafw'

    @property
    def redis_url(self) -> str:
        url = f'redis://{self.redis_host}:{self.redis_port}/{self.redis_db}'
        if self.redis_password:
            url = f'redis://{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}'
        return url
    
    @property
    def _postgres_path(self) -> str:
        return f'{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}'
    
    @property
    def sync_postgres_url(self) -> str:
        return f'postgresql://{self._postgres_path}'
    
    @property
    def async_postgres_url(self) -> str:
        return f'postgresql+asyncpg://{self._postgres_path}'
    

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

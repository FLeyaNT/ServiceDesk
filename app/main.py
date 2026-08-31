import uvicorn

from fastapi import (
    FastAPI,
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from redis_om import Migrator

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from pathlib import Path

from core.config import get_settings
from core.dependencies import (
    get_pg_engine,
)
from core.redis_client import redis_client
from core.exceptions import init_exceptions
from api.router import api_router


BASE_DIR = Path(__file__).parent


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    pg_engine = get_pg_engine()
    Migrator().run()
    
    yield
    await pg_engine.dispose()
    await redis_client.close()


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description=settings.description,
    lifespan=lifespan
)


init_exceptions(app)


app.include_router(api_router, prefix='/api')


@app.get('/status')
def get_status():
    return {
        'status': 'ok'
    }


app.mount(
    "/static", 
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)


@app.get("/")
async def serve_frontend():
    return FileResponse(str(BASE_DIR / "static/index.html"))


if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        reload=True,
        port=8000
    )

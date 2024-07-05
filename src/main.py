# FastAPI ecosystem
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Redis ecosystem
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis
from redis import Redis

# Local modules
from src.dht11.router import router as dht11_router
from src.fc28.router import router as fc28_router
from src.pages.router import router as pages_router

from src.config import settings

# Utils
import time


redis: Redis | None


# Event-Manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis
    # Startup
    redis = aioredis.from_url(settings.redis_url)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
    # Shutdown
    await redis.close()


app = FastAPI(
    title="Measurements-Srvice",
    description="### Service for saving and real-time streaming data from FC28 and DHT11 modules_",
    lifespan=lifespan,
    docs_url="/docs",
)

origins = [
    'http://localhost',
    'https://localhost',
]

# Cors settings
# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "WS"],
    allow_headers=["*"],
)

# Routers
app.include_router(dht11_router)
app.include_router(fc28_router)
app.include_router(pages_router)


# Moc cache
@app.get("/moc-transactions")
@cache(expire=5)
async def long_translation():
    time.sleep(5)
    return {
        "ok": True,
        "message": "Successful test cache at long operations"
    }

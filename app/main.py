from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from redis import asyncio as aioredis
from app.urls import register_routers
from app.utils.exeptions import CustomApiException, custom_api_exception_handler

app = FastAPI(title="app", debug=True)

register_routers(app)

app.add_exception_handler(CustomApiException, custom_api_exception_handler)


@app.on_event("startup")
async def startup_event():
    redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

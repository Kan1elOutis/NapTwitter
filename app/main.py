from fastapi import FastAPI, Depends
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_users import FastAPIUsers

from redis import asyncio as aioredis
from app.urls import register_routers
from app.utils.exeptions import CustomApiException, custom_api_exception_handler
from app.auth.auth import auth_backend

from app.auth.manager import get_user_manager
from app.auth.schemas import UserRead, UserCreate
from app.models.users import User

app = FastAPI(title="app", debug=True)


def create_app() -> FastAPI:
    app = FastAPI(title="app", debug=True)
    register_routers(app)

    app.add_exception_handler(CustomApiException, custom_api_exception_handler)
    return app


register_routers(app)

app.add_exception_handler(CustomApiException, custom_api_exception_handler)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

current_user = fastapi_users.current_user()


@app.get("/protected-route")
def protected_route(user: User = Depends(current_user)):
    return f"Hello, {user.username}"


@app.get("/unprotected-route")
def unprotected_route():
    return f"Hello, anonym"


@app.on_event("startup")
async def startup_event():
    redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

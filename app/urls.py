from fastapi import FastAPI

from app.routes.user import router as user_router
from app.routes.tweet import router as tweet_router


def register_routers(app: FastAPI) -> FastAPI:
    """
    Регистрация роутов для API
    """

    app.include_router(user_router)  # Вывод информации о пользователе
    app.include_router(tweet_router)  # Добавление, удаление и вывод твитов

    return app

from http import HTTPStatus
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.schemas.base_response import ResponseSchema
from app.schemas.like import LikeSchema
from app.schemas.user import UserSchema
from app.utils.exeptions import CustomApiException


class TweetInSchema(BaseModel):
    """
    Схема для входных данных при добавлении нового твита
    """

    tweet_data: str = Field()

    @field_validator("tweet_data", mode="before")
    @classmethod
    def check_len_tweet_data(cls, val: str) -> str | None:
        """
        Проверка длины твита с переопределением вывода ошибки в случае превышения
        """
        if len(val) > 280:
            raise CustomApiException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,  # 422
                detail=f"The length of the tweet should not exceed 280 characters. "
                       f"Current value: {len(val)}",
            )

        return val

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,  # Использовать псевдоним вместо названия поля
    )


class TweetResponseSchema(ResponseSchema):
    """
    Схема для вывода id твита после публикации
    """

    id: int = Field(alias="tweet_id")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,  # Использовать псевдоним вместо названия поля
    )


class TweetOutSchema(BaseModel):
    """
    Схема для вывода твита, автора, вложенных изображений и данных по лайкам
    """

    id: int
    tweet_data: str = Field(alias="content")
    user: UserSchema = Field(alias="author")
    likes: List[LikeSchema]

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,  # Использовать псевдоним вместо названия поля
    )


class TweetListSchema(ResponseSchema):
    """
    Схема для вывода списка твитов
    """

    tweets: List[TweetOutSchema]

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr

from app.schemas.base_response import ResponseSchema


class UserSchema(BaseModel):
    """
    Базовая схема для вывода основных данных о пользователе
    """

    id: int
    username: str = Field(alias="name")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class UserDataSchema(UserSchema):
    """
    Схема для вывода детальной информации о пользователе
    """

    following: Optional[List["UserSchema"]] = []
    followers: Optional[List["UserSchema"]] = []

    model_config = ConfigDict(from_attributes=True)


class UserOutSchema(ResponseSchema):
    """
    Схема для вывода ответа с детальными данными о пользователе
    """

    user: UserDataSchema


class EmailSchema(BaseModel):
    """
    :TODO
    """
    email: EmailStr
    subject: str = "Hello from FastAPI"
    body: str = "This is a test email sent from a background Celery task."


class UserBase(BaseModel):
    username: str
    email: str
    password: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool
    email_code: str


class UserCreate(BaseModel):
    email: str
    password: str
    re_password: str


class UserResult(BaseModel):
    username: str
    email: str
    is_active: bool
    is_superuser: bool
    is_verified: bool

    class Config:
        orm_mode = True


class UserActivationCreate(BaseModel):
    email: str
    activation_code: str

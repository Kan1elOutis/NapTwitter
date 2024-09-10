from typing import List
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.likes import Like
from app.models.tweets import Tweet

user_to_user = Table(
    "user_to_user",
    Base.metadata,
    Column("followers_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("following_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class User(Base):
    """
    Модель для хранения данных о пользователях
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    username: Mapped[str] = mapped_column(
        String(60), nullable=False, unique=True, index=True
    )
    api_key: Mapped[str] = mapped_column()
    tweets: Mapped[List["Tweet"]] = relationship(
        backref="user", cascade="all, delete-orphan"
    )
    likes: Mapped[List["Like"]] = relationship(
        backref="user",
        cascade="all, delete-orphan",
    )

    # Подписки пользователей друг на друга (многие ко многим)
    following = relationship(
        "User",
        secondary=user_to_user,
        primaryjoin=id == user_to_user.c.followers_id,
        secondaryjoin=id == user_to_user.c.following_id,
        backref="followers",
        lazy="selectin",
    )

from typing import List
from datetime import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Column, ForeignKey, Integer, String, Table, Boolean, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.models.likes import Like
from app.models.tweets import Tweet


from app.database import Base


user_to_user = Table(
    "user_to_user",
    Base.metadata,
    Column("followers_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("following_id", Integer, ForeignKey("user.id"), primary_key=True),
)


class User(SQLAlchemyBaseUserTable[int], Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    username: Mapped[str] = mapped_column(
        String(60), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(
        String(120), nullable=False, unique=True, index=True)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow)
    hashed_password: Mapped[str] = mapped_column(
        String, nullable=False)
    email_code: Mapped[str] = mapped_column(
        String, nullable=False, default='empty')
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    tweets: Mapped[List["Tweet"]] = relationship(
        backref="user", cascade="all, delete-orphan"
    )
    likes: Mapped[List["Like"]] = relationship(
        backref="user",
        cascade="all, delete-orphan",
    )

    following = relationship(
        "User",
        secondary=user_to_user,
        primaryjoin=id == user_to_user.c.followers_id,
        secondaryjoin=id == user_to_user.c.following_id,
        backref="followers",
        lazy="selectin",
    )

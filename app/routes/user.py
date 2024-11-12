from typing import Annotated
from datetime import datetime, timedelta
import secrets
import socket
import random
from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.tasks import send_async_email_task
from app.database import get_async_session
from app.models.users import User
from app.services.user import UserService
from app.services.follower import FollowerService
from app.utils.user import get_current_user
from app.utils.exeptions import CustomApiException
from app.schemas.user import UserOutSchema, EmailSchema, UserResult, UserCreate, UserActivationCreate
from app.schemas.base_response import (
    UnauthorizedResponseSchema,
    ErrorResponseSchema,
    ValidationResponseSchema,
    ResponseSchema,
    LockedResponseSchema,
)
from passlib.hash import bcrypt

from dotenv import load_dotenv

from app.database import get_async_session_user

load_dotenv('.env')

router = APIRouter(
    prefix="/api/users", tags=["users"]
)


@router.get(
    "/me",
    response_model=UserOutSchema,
    responses={401: {"model": UnauthorizedResponseSchema}},
    status_code=200,
)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Вывод данных о текущем пользователе: id, username, подписки, подписчики
    """
    return {"user": current_user}


@router.post(
    "/{user_id}/follow",
    response_model=ResponseSchema,
    responses={
        401: {"model": UnauthorizedResponseSchema},
        404: {"model": ErrorResponseSchema},
        422: {"model": ValidationResponseSchema},
        423: {"model": LockedResponseSchema},
    },
    status_code=201,
)
async def create_follower(
        user_id: int,
        current_user: Annotated[User, Depends(get_current_user)],
        session: AsyncSession = Depends(get_async_session),
):
    """
    Подписка на пользователя
    """
    await FollowerService.create_follower(
        current_user=current_user, following_user_id=user_id, session=session
    )

    return {"result": True}


@router.delete(
    "/{user_id}/follow",
    response_model=ResponseSchema,
    responses={
        401: {"model": UnauthorizedResponseSchema},
        404: {"model": ErrorResponseSchema},
        422: {"model": ValidationResponseSchema},
        423: {"model": LockedResponseSchema},
    },
    status_code=200,
)
async def delete_follower(
        user_id: int,
        current_user: Annotated[User, Depends(get_current_user)],
        session: AsyncSession = Depends(get_async_session),
):
    """
    Отписка от пользователя
    """
    await FollowerService.delete_follower(
        current_user=current_user, followed_user_id=user_id, session=session
    )

    return {"result": True}


@router.get(
    "/{user_id}",
    response_model=UserOutSchema,
    responses={
        401: {"model": UnauthorizedResponseSchema},
        404: {"model": ErrorResponseSchema},
        422: {"model": ValidationResponseSchema},
        423: {"model": LockedResponseSchema},
    },
    status_code=200,
)
async def get_user(user_id: int, session: AsyncSession = Depends(get_async_session)):
    """
    Вывод данных о пользователе: id, username, подписки, подписчики
    """
    user = await UserService.get_user_for_id(user_id=user_id, session=session)

    if user is None:
        raise CustomApiException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        )

    return {"user": user}


@router.put('/user/create', response_model=UserResult)
async def create_user(req: UserCreate, db: AsyncSession = Depends(get_async_session_user)):
    email_code = ''.join([str(secrets.randbelow(10)) for _ in range(8)])
    if req.re_password != req.password:
        raise HTTPException(detail="Password do not match, try again", status_code=status.HTTP_406_NOT_ACCEPTABLE)

    stmt = select(User).where(
        User.email == req.email.lower(),
        User.is_verified.is_(True),
        User.is_active.is_(True)
    )
    result = await db.execute(stmt)
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_421_MISDIRECTED_REQUEST,
            detail=f"User  email - {req.email.lower()} already exists, try login"
        )

    stmt = select(User).where(
        User.email == req.email.lower(),
        User.is_verified.is_(False),
        User.is_active.is_(True)
    )
    result = await db.execute(stmt)
    expired_user = result.scalars().first()

    if expired_user:
        stmt = update(User).where(User.email == req.email.lower()).values(
            email_code=email_code
        )
        await db.execute(stmt)
        await db.commit()

        send_async_email_task.delay(req.email.lower(), "Account Activation Code", {"msg": email_code, "email": req.email})
        raise HTTPException(
            status_code=status.HTTP_206_PARTIAL_CONTENT,
            detail=f"Account ID exists, please verify, we've resent new code to {req.email}"
        )

    stmt = select(User).where(
        User.email == req.email.lower(),
        User.is_verified.is_(False),
        User.is_active.is_(True)
    )
    result = await db.execute(stmt)
    active_user = result.scalars().first()

    if active_user:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail="Please, we've to wait for the elapse time")

    stmt = select(User).where(
        User.email == req.email.lower(),
        User.is_verified.is_(True),
        User.is_active.is_(False)
    )
    result = await db.execute(stmt)
    blocked_user = result.scalars().first()

    if blocked_user:
        raise HTTPException(
            detail="Account Blocked!",
            status_code=status.HTTP_403_FORBIDDEN
        )

    new_user = User(
        username="user-" + secrets.token_urlsafe(6),
        email=req.email.lower(),
        hashed_password=bcrypt.hash(req.password),
        email_code=email_code,
        is_superuser=False,
        is_verified=False,
        is_active=True
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    send_async_email_task.delay(req.email.lower(), "Account Activation Code", {"msg": email_code, "email": req.email})

    return new_user


@router.post('/user/activation')
async def account_activation(req: UserActivationCreate,
                             db: AsyncSession = Depends(get_async_session_user)) -> JSONResponse:
    if not req:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No activation code found")

    result = await db.execute(
        select(User).filter(
            User.email == req.email.lower(),
            User.email_code == req.activation_code
        )
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Token expired...request for new code"
        )

    invalid_credentials_check = await db.execute(
        select(User).filter(
            (User.email != req.email.lower()) |
            (User.email_code != req.activation_code)
        )
    )
    if invalid_credentials_check.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Invalid Credential, try again"
        )

    user.is_verified = True
    user.is_active = True
    db.add(user)
    await db.commit()

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "message": "Your account was successfully activated",
        }
    )

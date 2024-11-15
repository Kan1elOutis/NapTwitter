from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from http import HTTPStatus
from loguru import logger

from app.models.likes import Like
from app.models.tweets import Tweet
from app.models.users import User
from app.utils.exeptions import CustomApiException
from app.schemas.tweet import TweetInSchema


class TweetsService:
    """
    Сервис для добавления, удаления и вывода твитов
    """

    @classmethod
    async def get_tweets(cls, user: User, session: AsyncSession):
        """
        Вывод последних твитов подписанных пользователей
        :param user: объект текущего пользователя
        :param session: объект асинхронной сессии
        :return: список с твитами
        """
        logger.debug("Вывод твитов")

        query = (
            select(Tweet)
            .filter(Tweet.user_id.in_(user.id for user in user.following))
            .options(
                joinedload(Tweet.user),
                joinedload(Tweet.likes).subqueryload(Like.user)
            )
            .order_by(Tweet.created_at.desc())
        )

        result = await session.execute(query)
        tweets = result.unique().scalars().all()

        return tweets

    @classmethod
    async def get_tweet(cls, tweet_id: int, session: AsyncSession) -> Tweet | None:
        """
        Возврат твита по переданному id
        :param tweet_id: id твита для поиска
        :param session: объект асинхронной сессии
        :return: объект твита
        """
        logger.debug(f"Поиск твита по id: {tweet_id}")

        query = select(Tweet).where(Tweet.id == tweet_id)
        tweet = await session.execute(query)

        return tweet.scalar_one_or_none()

    @classmethod
    async def create_tweet(
        cls, tweet: TweetInSchema, current_user: User, session: AsyncSession
    ) -> Tweet:
        """
        Создание нового твита
        :param tweet: данные для нового твита
        :param current_user: объект текущего пользователя
        :param session: объект асинхронной сессии
        :return: объект нового твита
        """
        logger.debug("Добавление нового твита")

        new_tweet = Tweet(tweet_data=tweet.tweet_data, user_id=current_user.id)

        session.add(new_tweet)
        await session.flush()

        await session.commit()

        return new_tweet

    @classmethod
    async def delete_tweet(
        cls, user: User, tweet_id: int, session: AsyncSession
    ) -> None:
        """
        Удаление твита
        :param user: объект текущего пользователя
        :param tweet_id: id удаляемого твита
        :param session: объект асинхронной сессии
        :return: None
        """
        logger.debug(f"Удаление твита")

        tweet = await cls.get_tweet(tweet_id=tweet_id, session=session)

        if not tweet:
            logger.error("Твит не найден")

            raise CustomApiException(
                status_code=HTTPStatus.NOT_FOUND, detail="Tweet not found"  # 404
            )

        else:
            if tweet.user_id != user.id:
                logger.error("Запрос на удаление чужого твита")

                raise CustomApiException(
                    status_code=HTTPStatus.LOCKED,  # 423
                    detail="The tweet that is being accessed is locked",
                )

            else:
                await session.delete(tweet)
                await session.commit()
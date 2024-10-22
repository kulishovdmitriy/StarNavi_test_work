from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.database.db import get_database


async def get_user_db(session: AsyncSession = Depends(get_database)):
    """
    :param session: An instance of AsyncSession that is injected using FastAPI's Depends. This session is required to interact with the SQLAlchemy database.
    :return: An instance of SQLAlchemyUserDatabase initialized with the provided session and User model.
    """

    yield SQLAlchemyUserDatabase(session, User)

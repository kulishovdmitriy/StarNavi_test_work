from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.database.db import get_database


async def get_user_db(session: AsyncSession = Depends(get_database)):
    yield SQLAlchemyUserDatabase(session, User)

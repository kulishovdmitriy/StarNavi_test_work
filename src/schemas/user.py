import uuid
from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):

    username: str
    auto_reply_enabled: bool
    reply_delay_minutes: int


class UserCreate(schemas.BaseUserCreate):

    username: str
    auto_reply_enabled: bool
    reply_delay_minutes: int


class UserUpdate(schemas.BaseUserUpdate):

    username: str
    auto_reply_enabled: bool
    reply_delay_minutes: int

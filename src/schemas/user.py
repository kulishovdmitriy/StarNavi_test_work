import uuid
from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    """
    Represents a read-only user with UUID as the identifier.
    The UserRead class extends the BaseUser class with additional attributes.

    Attributes:
        username (str): The username of the user.
        auto_reply_enabled (bool): Indicates if auto-reply is enabled for the user.
        reply_delay_minutes (int): The delay in minutes before the auto-reply is sent.
    """

    username: str
    auto_reply_enabled: bool
    reply_delay_minutes: int


class UserCreate(schemas.BaseUserCreate):
    """
    User creation schema extending BaseUserCreate.

    Attributes
    ----------
    username: str
        The username of the new user.
    auto_reply_enabled: bool
        Flag indicating if the auto-reply feature is enabled for the user.
    reply_delay_minutes: int
        The delay in minutes before an auto-reply message is sent.
    """

    username: str
    auto_reply_enabled: bool
    reply_delay_minutes: int


class UserUpdate(schemas.BaseUserUpdate):
    """
    UserUpdate class extends BaseUserUpdate.

    Attributes:
        username (str): The username of the user.
        auto_reply_enabled (bool): Indicates whether auto-reply is enabled.
        reply_delay_minutes (int): Specifies the delay in minutes for auto-reply.
    """

    username: str
    auto_reply_enabled: bool
    reply_delay_minutes: int

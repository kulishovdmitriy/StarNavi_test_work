import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase

from src.entity.models import User
from src.database.user_db import get_user_db
from src.conf.config import settings


SECRET_KEY_JWT = settings.SECRET_KEY_JWT


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """
    UserManager class used for managing user-related functionalities.

    Inherits:
        UUIDIDMixin
        BaseUserManager[User, uuid.UUID]

    Attributes:
        reset_password_token_secret (str): Secret key used for generating and verifying password reset tokens.
        verification_token_secret (str): Secret key used for generating and verifying user verification tokens.

    Methods:
        async on_after_register(user, request):
            Called after a user has registered. This logs the user ID as having registered.

        async on_after_forgot_password(user, token, request):
            Called after a user has requested password reset. Logs the user ID and the reset token.

        async on_after_request_verify(user, token, request):
            Called after a user has requested verification. Logs the user ID and the verification token.

    """

    reset_password_token_secret = SECRET_KEY_JWT
    verification_token_secret = SECRET_KEY_JWT

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    """
    Dependency that provides an instance of UserManager.

    This function is an asynchronous generator that yields a UserManager instance,
    initialized with the provided SQLAlchemyUserDatabase.

    :param user_db: The database dependency providing access to the SQLAlchemyUserDatabase instance.

    :type user_db: SQLAlchemyUserDatabase
    :yield: An instance of UserManager.
    :rtype: UserManager

    """

    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    """
    Creates and returns a JWT strategy for handling JSON Web Tokens.

    This function initializes the JWTStrategy class with the specified secret key
    and a lifetime of 3600 seconds (1 hour). It can be used for generating and
    validating JWTs in the authentication process.

    :return: An instance of the JWTStrategy class initialized with a secret key
             and a lifetime of 3600 seconds.

    :rtype: JWTStrategy

    """

    return JWTStrategy(secret=SECRET_KEY_JWT, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)

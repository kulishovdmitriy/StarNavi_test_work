import asyncio
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from fastapi_users.password import PasswordHelper
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from main import app
from src.entity.models import Base, User
from src.database.db import get_database
from src.conf.config import settings
from src.services.logger import setup_logger


logger = setup_logger(__name__)

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

test_user = {"id": "user-id", "username": "deadpool", "email": "deadpool@example.com", "password": "123456789"}

SECRET = settings.SECRET_KEY_JWT


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            password_helper = PasswordHelper()
            hashed_password = password_helper.hash(test_user['password'])
            current_user = User(username=test_user['username'], email=test_user['email'], hashed_password=hashed_password,
                                auto_reply_enabled=False, reply_delay_minutes=0, is_active=True, is_verified=True)
            session.add(current_user)
            await session.commit()
            await session.refresh(current_user)

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    # Dependency override

    async def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        except Exception as err:
            logger.error(f"Error work database: {err}")
            await session.rollback()
            raise
        finally:
            await session.close()

    app.dependency_overrides[get_database] = override_get_db

    yield TestClient(app)


@pytest_asyncio.fixture(scope="module")
async def get_token(client):

    response = client.post('auth/jwt/login', data={"username": "deadpool@example.com", "password": "123456789"})
    logger.info(f"{response}")
    assert response.status_code == 200, response.text
    return response.json().get("access_token")

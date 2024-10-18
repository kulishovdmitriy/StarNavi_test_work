from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from dotenv import load_dotenv


load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    model_config = ConfigDict(extra='ignore', env_file='.env', env_file_encoding="utf-8")  # noqa


settings = Settings()

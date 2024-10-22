from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from dotenv import load_dotenv


load_dotenv()


class Settings(BaseSettings):
    """
    Settings class to handle environment variables for the application.

    Attributes:
        DATABASE_URL (str): The full URL to connect to the database.
        POSTGRES_DB (str): The name of the Postgres database.
        POSTGRES_USER (str): The username for the Postgres database.
        POSTGRES_PASSWORD (str): The password for the Postgres database.
        POSTGRES_HOST (str): The host address for the Postgres database.
        POSTGRES_PORT (str): The port number for the Postgres database.

        SECRET_KEY_JWT (str): The secret key used for JWT encoding and decoding.

        GOOGLE_APPLICATION_CREDENTIALS (str): The file path to Google Cloud service account credentials.
        TOKEN_AUTH (str): Token used for authentication.

    Configuration:
        model_config (ConfigDict): Configurations for handling environment files and encoding.
    """

    DATABASE_URL: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    SECRET_KEY_JWT: str

    GOOGLE_APPLICATION_CREDENTIALS: str
    TOKEN_AUTH: str

    model_config = ConfigDict(extra='ignore', env_file='.env', env_file_encoding="utf-8")  # noqa


settings = Settings()

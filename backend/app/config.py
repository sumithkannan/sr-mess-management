import os

from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    APP_NAME: str = "Mess Management"
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'mess.db')}"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    # Business timezone used to interpret meal start/end times.
    # Servers (e.g. PythonAnywhere) run in UTC, so windows must not use the
    # server's local clock.
    TIMEZONE: str = "Asia/Kolkata"

    class Config:
        env_file = os.path.join(BASE_DIR, ".env")


settings = Settings()
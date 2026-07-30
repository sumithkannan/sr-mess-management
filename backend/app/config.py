from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Mess Management"
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = "sqlite:///./mess.db"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    class Config:
        env_file = ".env"

settings = Settings()

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Blog Platform API"
    DEBUG: bool = True

    DATABASE_URL: str = "postgresql://pfaldb:pfaldb@localhost:5432/pfaldb"

    SECRET_KEY: str = "change-this-to-a-long-random-secret-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Comma-separated list of allowed origins, e.g. "https://myblog.com,https://www.myblog.com"
    # Defaults to "*" for easy local dev; set explicitly in production.
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"


settings = Settings()

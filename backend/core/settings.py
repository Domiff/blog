from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings as _BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).parent.parent.parent


class BaseSettings(_BaseSettings):
    IS_DEBUG: bool = Field(default=True)

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class AppSettings(BaseSettings):
    APP_NAME: str = "Blog"
    APP_TITLE: str = "Blog API"
    APP_VERSION: str = "1"


class DBSettings(BaseSettings):
    DB_URL: str = ""
    SQLITE_URL: str = "sqlite+aiosqlite:///db.sqlite3"

    POSTGRES_DB: str = "POSTGRES_DB"
    POSTGRES_USER: str = "POSTGRES_USER"
    POSTGRES_PASSWORD: str = "POSTGRES_PASSWORD"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    def get_pg_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def model_post_init(self, __context) -> None:
        if not self.DB_URL:
            object.__setattr__(
                self,
                "DB_URL",
                self.SQLITE_URL if self.IS_DEBUG else self.get_pg_url(),
            )


class CORSSettings(BaseSettings):
    CORS_ORIGINS: list[str] = ["127.0.0.1", "localhost"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]


class LoggingSettings(BaseSettings):
    LOG_LEVEL: str = "INFO"


class AdminSettings(BaseSettings):
    ADMIN_SECRET_KEY: str
    ADMIN_BASE_URL: str = "/admin"


class AuthSettings(BaseSettings):
    JWT_PRIVATE_KEY: Path = BASE_DIR / "keys" / "jwt-private.pem"
    JWT_PUBLIC_KEY: Path = BASE_DIR / "keys" / "jwt-public.pem"
    JWT_ALGORITHM: str = "RS256"
    JWT_ACCESS_TOKEN_EXPIRES: int = 15
    JWT_REFRESH_TOKEN_EXPIRES: int = 30


class RedisSettings(AppSettings):
    REDIS_URL: str = ""
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CONNECTION_POOL_MAXSIZE: int = 10
    EXPIRE: int = 60 * 60

    def model_post_init(self, __context) -> None:
        if not self.REDIS_URL:
            self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


class Settings:
    app: AppSettings = AppSettings()
    cors: CORSSettings = CORSSettings()
    db: DBSettings = DBSettings()
    logging: LoggingSettings = LoggingSettings()
    admin: AdminSettings = AdminSettings()
    auth: AuthSettings = AuthSettings()
    redis: RedisSettings = RedisSettings()


settings = Settings()

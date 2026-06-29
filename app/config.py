from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str = Field(default="localhost")
    DB_PORT: int = Field(default=5432)
    DB_USER: str = Field(default="postgres")
    DB_PASS: str = Field(default="")
    DB_NAME: str = Field(default="postgres")
    TESTDB_NAME: str = Field(default="test_library_db")

    @property
    def TESTDATABASE_URL_psycopg(self):
        return (
            f"postgresql+psycopg_async://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.TESTDB_NAME}"
        )

    @property
    def DATABASE_URL_psycopg_async(self):
        # DSN
        # postgresql(СУБД_название)+psycopg(ЛИБА_название)://user_name:pass@host:port/db_name
        return f"postgresql+psycopg_async://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL_psycopg(self):
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    JWT_SECRET_KEY: str = Field(default="super_secret_123456789")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_USERNAME: Optional[str] = "postgres"
    POSTGRES_PASSWORD: Optional[str] ="postgres"
    POSTGRES_HOST: Optional[str] = "localhost:5432"
    POSTGRES_DBNAME: Optional[str] = "TheftBlock"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

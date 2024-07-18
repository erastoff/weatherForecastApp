from functools import lru_cache
from typing import final
from decouple import config
from pydantic_settings import BaseSettings, SettingsConfigDict


@final
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".prod.env", ".dev.env"),  # first search .dev.env, then .prod.env
        env_file_encoding="utf-8",
    )
    OWM_API_KEY: str = config("OWM_API_KEY")


@lru_cache()  # get it from memory
def get_settings() -> Settings:
    return Settings()

# pydantic_settings isn't installed in the current environment, and
# pydantic's own BaseSettings works for our simple needs.
from pydantic import BaseSettings


class Settings(BaseSettings):
    OPEN_API_KEY: str
    OPEN_MODEL: str = "gpt-5-mini"

    class Config:
        env_file = ".env"


settings = Settings()
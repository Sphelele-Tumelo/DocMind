# Pydantic v2 moved BaseSettings into the pydantic-settings package.
# Install it in the environment and import from there to avoid errors.
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPEN_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"


settings = Settings()
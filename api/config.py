# Pydantic v2 moved BaseSettings into the pydantic-settings package.
# Install it in the environment and import from there to avoid errors.
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-1.5-flash"

    class Config:
        env_file = ".env"


settings = Settings()
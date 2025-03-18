import logging

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    bot_token: str
    search_url_sens: str

    log_level: str = "INFO"

    def get_log_level(self) -> int:
        return {
            "info": logging.INFO,
            "debug": logging.DEBUG,
            "error": logging.ERROR,
        }.get(self.log_level.lower(), logging.INFO)

    class Config:
        env_file = ".env"


settings = Settings()

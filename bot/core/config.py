import logging

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    search_url_sens: str
    selenium_url: str
    selenium_status_url: str
    search_url_yakaboo: str
    search_url_readeat: str
    search_url_eknygarnya: str
    search_url_zhupansky: str
    search_url_bookling: str
    search_url_ksd: str
    redis_host: str
    redis_port: int

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

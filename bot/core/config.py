import logging

import colorlog
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
    search_url_vivat: str
    api_search_url_old_lion: str
    search_url_old_lion: str
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


def setup_logging():
    log_colors = {
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    }

    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        log_colors=log_colors,
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.get_log_level())
    root_logger.addHandler(handler)


settings = Settings()
setup_logging()

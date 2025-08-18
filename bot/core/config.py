import logging
import os
from typing import Optional
from urllib.parse import quote

import colorlog
from pydantic import PostgresDsn, RedisDsn, SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_db: str
    postgres_user: SecretStr
    postgres_password: SecretStr

    db_host: str = "db"
    echo_query: bool = True  # just for dev
    db_port: int = 5432

    redis_host: str = "redis"
    redis_scheme: str
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[SecretStr] = None

    bot_token: str
    server_port: int

    search_url_sens: str
    search_url_eknygarnya: str
    search_url_yakaboo: str
    search_url_zhupansky: str
    search_url_bookling: str
    search_api_url_readeat: str
    base_url_readeat: str
    search_url_ksd: str
    search_url_vivat: str
    api_search_url_old_lion: str
    search_url_old_lion: str
    search_url_mbooks: str
    base_url_mbooks: str
    search_url_fabula: str
    google_book_api_key: str
    google_rating: str
    webhook_base_url: str

    log_level: str = "INFO"

    def get_log_level(self) -> int:
        levels = {
            "info": logging.INFO,
            "debug": logging.DEBUG,
            "error": logging.ERROR,
            "warning": logging.WARNING,
            "critical": logging.CRITICAL,
        }
        return levels.get(self.log_level.lower(), logging.INFO)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def db_connection_uri(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            path=f"{self.postgres_db}",
            username=self.postgres_user.get_secret_value(),
            password=quote(self.postgres_password.get_secret_value()),
        )

    @property
    def redis_connection_uri(self) -> str:
        scheme = os.getenv("REDIS_SCHEME", "redis")
        return str(
            RedisDsn.build(
                scheme=scheme,
                host=self.redis_host,
                port=self.redis_port,
                password=(
                    self.redis_password.get_secret_value()
                    if self.redis_password
                    else None
                ),
                path=f"/{self.redis_db}",
            )
        )

    @property
    def webhook_url(self) -> str:
        return f"{self.webhook_base_url}/webhook"


def create_color_formatter() -> logging.Formatter:
    log_colors = {
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    }
    return colorlog.ColoredFormatter(
        fmt="%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        log_colors=log_colors,
    )


def setup_logging(log_level: int):
    handler = logging.StreamHandler()
    handler.setFormatter(create_color_formatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)


settings = Settings()
setup_logging(settings.get_log_level())

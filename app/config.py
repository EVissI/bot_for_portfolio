import os
from typing import List
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
import redis.asyncio as aioredis


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    ADMIN_IDS: list[int]
    BASE_SITE_URL: str 
    PORT:int = 8000
    FORMAT_LOG: str = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"
    LOG_ROTATION: str = "10 MB"
    DB_URL: str = 'sqlite+aiosqlite:///app/data/db.sqlite3'
    class Config:
        case_sensitive = False,
        env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    def get_webhook_url(self) -> str:
        """Возвращает URL вебхука с кодированием специальных символов."""
        return f"{self.BASE_SITE_URL}/webhook"

settings = Settings()


log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.txt")
logger.add(log_file_path, format=settings.FORMAT_LOG, level="INFO", rotation=settings.LOG_ROTATION)
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log_error.txt")
logger.add(log_file_path, format=settings.FORMAT_LOG, level="ERROR", rotation=settings.LOG_ROTATION)

    #редис может понадобиться для хранения fsm состояния
# redis = aioredis.from_url(
#         settings.redis.url
#     )
bot = Bot(token=settings.BOT_TOKEN.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# dp = Dispatcher(storage=RedisStorage(redis))

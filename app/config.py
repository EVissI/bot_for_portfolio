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
    BOT_TOKEN: SecretStr = ''
    ADMIN_IDS: List[int] = []
    BASE_SITE_URL: str = ''
    PORT:int = 8000
    FORMAT_LOG: str = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"
    LOG_ROTATION: str = "10 MB"
    DB_URL: str = 'sqlite+aiosqlite:///app/data/db.sqlite3'
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )
    def get_webhook_url(self) -> str:
        """Возвращает URL вебхука с кодированием специальных символов."""
        return f"{self.BASE_SITE_URL}/webhook"

settings = Settings()
#редис может понадобиться для хранения fsm состояния
# redis = aioredis.from_url(
#         settings.redis.url
#     )
try:
    bot = Bot(token=settings.BOT_TOKEN.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
except Exception as e:
    logger.error('Ошибка инициализации бота: ' + str(e))
# dp = Dispatcher(storage=RedisStorage(redis))

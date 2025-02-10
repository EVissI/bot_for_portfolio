import os
from typing import List
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from pydantic import SecretStr,BaseModel, RedisDsn, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
import redis.asyncio as aioredis
from contextlib import asynccontextmanager


class BotConfig(BaseModel):
    bot_token:SecretStr
    admin_ids:List[int]

class RedisConfig(BaseModel):
    url:RedisDsn

class LogSettings(BaseModel):
    format_log: str = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"
    log_rotation: str = "10 MB"

class FastApiConfig(BaseModel):
    url: str

class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080

class Settings(BaseSettings):
    bot:BotConfig
    run: RunConfig = RunConfig()
    redis:RedisConfig
    db_url: str = 'sqlite+aiosqlite:///data/db.sqlite3'
    log:LogSettings = LogSettings()
    fastapi:FastApiConfig
    model_config = SettingsConfigDict(
        case_sensitive=False,   
        env_nested_delimiter= "__",
        env_prefix="APP_CONFIG__",
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )
    def get_webhook_url(self) -> str:
        """Возвращает URL вебхука с кодированием специальных символов."""
        return f"{self.fastapi.url}/webhook"
    
settings = Settings()
#редис может понадобиться для хранения fsm состояния
redis = aioredis.from_url(
        settings.redis.url
    )

bot = Bot(token=settings.bot.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
# dp = Dispatcher(storage=RedisStorage(redis))
from loguru import logger
from fastapi import FastAPI
from contextlib import asynccontextmanager
from aiogram.types import BotCommand, BotCommandScopeDefault

from config import bot,dp
from config import settings
from bot.middlewares.anti_floud import AntiFloudMiddleware

# Функция, которая настроит командное меню (дефолтное для всех пользователей)
async def set_commands():
    commands = [BotCommand(command='start', description='Старт')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())

admins = settings.bot.admin_ids
# Функция, которая выполнится когда бот запустится
async def start_bot():
    await set_commands()
    for admin_id in admins:
        try:
            await bot.send_message(admin_id, f'Я запущен🥳.')
        except:
            pass
    logger.info("Бот успешно запущен.")


# Функция, которая выполнится когда бот завершит свою работу
async def stop_bot():
    try:
        for admin_id in admins:
            await bot.send_message(admin_id, 'Бот остановлен. За что?😔')
    except:
        pass
    logger.error("Бот остановлен!")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting bot setup...")
    #регистрация middleware
    dp.message.middleware(AntiFloudMiddleware(1))
    #регистрация роутеров
    # dp.include_router(user_router)
    await start_bot()
    webhook_url = settings.get_webhook_url()
    await bot.set_webhook(url=webhook_url,
                        allowed_updates=dp.resolve_used_update_types(),
                        drop_pending_updates=True)
    logger.info(f"Webhook set to {webhook_url}")
    yield
    logger.info("Shutting down bot...")
    await bot.delete_webhook()
    await stop_bot()
    logger.info("Webhook deleted")
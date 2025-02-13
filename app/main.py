import os
import uvicorn
from loguru import logger
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.types import Update

from config import bot,dp,settings
from bot.middlewares.is_admin import CheckIsAdmin
from bot.middlewares.anti_floud import AntiFloudMiddleware
from bot.users.router import user_router
from bot.admin.routers.main_router import admin_router

app = FastAPI()
# Функция, которая настроит командное меню (дефолтное для всех пользователей)
async def set_commands():
    commands = [BotCommand(command='start', description='Старт')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())

root_admin = settings.ROOT_ADMIN_ID
# Функция, которая выполнится когда бот запустится
async def start_bot():
    await set_commands()
    try:
        pass
        # await bot.send_message(root_admin, f'Я запущен🥳.')
    except:
        pass
    logger.info("Бот успешно запущен.")


# Функция, которая выполнится когда бот завершит свою работу
async def stop_bot():
    try:
        pass
        # await bot.send_message(root_admin, 'Бот остановлен. За что?😔')
    except:
        pass
    logger.error("Бот остановлен!")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting bot setup...")
    #регистрация middleware
    admin_router.message.middleware(CheckIsAdmin())
    dp.message.middleware(AntiFloudMiddleware(1))
    #регистрация роутеров
    dp.include_router(user_router)
    dp.include_router(admin_router)
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

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def webhook(request: Request) -> None:
    logger.info("Received webhook request")
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    logger.info("Update processed")

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True,reload_delay=3,port=settings.PORT,env_file= f"{settings.BASE_DIR}/.env")
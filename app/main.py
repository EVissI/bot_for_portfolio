import os
import ssl
import uvicorn
from loguru import logger
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.types import Update,FSInputFile
from config import bot,dp,settings
from bot.middlewares.is_admin import CheckIsAdmin
from bot.middlewares.anti_floud import AntiFloudMiddleware
from bot.users.router import user_router
from bot.admin.routers.main_router import admin_router

app = FastAPI()
async def set_commands():
    commands = [BotCommand(command='start', description='Старт'),BotCommand(command='contact', description='контакты'),BotCommand(command='my_projects', description='мои проекты')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())

root_admins = settings.ROOT_ADMIN_IDS
async def start_bot():
    await set_commands()
    try:
        for admin in root_admins:
            await bot.send_message(admin, f'Я запущен🥳.')
    except:
        pass
    logger.info("Бот успешно запущен.")


async def stop_bot():
    try:
        for admin in root_admins:
            await bot.send_message(admin, 'Бот остановлен. За что?😔')
    except:
        pass
    logger.error("Бот остановлен!")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting bot setup...")
    admin_router.message.middleware(CheckIsAdmin())
    dp.message.middleware(AntiFloudMiddleware(1))
    dp.include_router(admin_router)
    dp.include_router(user_router)
    await start_bot()   
    await dp.start_polling(bot,
                        drop_pending_updates=True,
                        allowed_updates=dp.resolve_used_update_types())
    yield 
    await dp.stop_polling()
    logger.info("Shutting down bot...")
    await stop_bot() 

app = FastAPI(lifespan=lifespan)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=False,reload_delay=3,port=settings.PORT,env_file= f"{settings.BASE_DIR}/.env")


import asyncio
from loguru import logger
from aiogram.types import BotCommand, BotCommandScopeDefault
from app.config import bot,dp,settings
from app.bot.middlewares.is_admin import CheckIsAdmin
from app.bot.middlewares.anti_floud import AntiFloudMiddleware
from app.bot.users.router import user_router
from app.bot.admin.routers.main_router import admin_router

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



async def main():
    logger.info("Starting bot setup...")
    admin_router.message.middleware(CheckIsAdmin())
    dp.message.middleware(AntiFloudMiddleware(0.5))
    dp.include_router(admin_router)
    dp.include_router(user_router)
    try:
        await start_bot()
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await stop_bot()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())


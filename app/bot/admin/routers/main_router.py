from aiogram import Router
from bot.admin.routers.create_router import create_project
from bot.admin.routers.delete_router import delete_project
from bot.admin.routers.update_router import update_project

admin_router = Router()
admin_router.include_router(create_project)
admin_router.include_router(delete_project)
admin_router.include_router(update_project)

from aiogram import Router
from bot.admin.routers.create_router import admin_router_create_project

admin_router = Router()
admin_router.include_router(admin_router_create_project)



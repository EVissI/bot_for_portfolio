from aiogram import F, Router
from aiogram.types import Message
from loguru import logger
from aiogram.filters import StateFilter

from bot.models import User
from bot.dao import UserDAO
from bot.keyboard.markup_kb import MainKeyboard
from dao.database import connection
from bot.admin.states import AdminPanelStates
admin_list_router = Router()

@admin_list_router.message(F.text == MainKeyboard.get_control_admins_kb().get('admin_list'),StateFilter(AdminPanelStates.admins_control))
@connection()
async def cmd_admin_list(message:Message,session,**kwargs):
    try:

        admins:list[User] = await UserDAO.get_admins(session)
        msg = ''
        for admin in admins:
            msg += f'{admin.first_name} [{admin.telegram_id}] \n'
        await message.answer(msg,reply_markup=MainKeyboard.build_admins_control_panel())

    except Exception as e:
        logger.error(
            f"Ошибка при получении списка админов: {e}"
        )
        await message.answer(
            "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова позже."
        )
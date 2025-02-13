from aiogram.dispatcher.router import Router
from aiogram import F
from aiogram.types import Message
from aiogram.filters import CommandObject, CommandStart

from loguru import logger

from bot.keyboard.markup_kb import MainKeyboard
from bot.models import User
from bot.schemas import TelegramIDModel, UserModel
from dao.database import connection
from bot.dao import UserDAO
from config import settings

from . import start_message

user_router = Router()

@user_router.message(CommandStart())
@connection()
async def cmd_start(message: Message, command: CommandObject, session, **kwargs):
    try:
        user_id = message.from_user.id
        user_info = await UserDAO.find_one_or_none(
            session=session, filters=TelegramIDModel(telegram_id=user_id)
        )
        if user_info:
            msg = start_message(message.from_user.first_name)
            await message.answer(msg, reply_markup=MainKeyboard.build(user_info.role))
            return
        if user_id == settings.ROOT_ADMIN_ID:
            values = UserModel(
                telegram_id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                role=User.Role.Admin,
            )
            await UserDAO.add(session=session, values=values)
            await message.answer(
                "Привет администрации", reply_markup=MainKeyboard.build(User.Role.Admin)
            )
            return
        values = UserModel(
            telegram_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            role=User.Role.User,
        )
        await UserDAO.add(session=session, values=values)
        msg = start_message(message.from_user.first_name)
        await message.answer(msg, reply_markup=MainKeyboard.build(User.Role.User))

    except Exception as e:
        logger.error(
            f"Ошибка при выполнении команды /start для пользователя {message.from_user.id}: {e}"
        )
        await message.answer(
            "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова позже."
        )

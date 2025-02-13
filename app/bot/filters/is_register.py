from aiogram.filters import BaseFilter
from typing import Any, Dict, Optional, Union
from aiogram.types import Message, User
from loguru import logger
from dao.database import async_session_maker
from bot.dao import UserDAO
from bot.models import User as UserModel

class IsRegisterFilter(BaseFilter):
    async def __call__(
        self,
        message: Message,
    ) -> Union[bool, UserModel]:
        async with async_session_maker() as session:
            logger.info(message.from_user.id)
            user_info:Optional[UserModel] = await UserDAO.find_by_telegram_id(session,message.from_user.id)
            if user_info:
                return {'user_info':user_info}
            else:
                await message.answer('Для использования ботом пройдите регистрацию через команду /start')
                return False
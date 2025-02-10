from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import Message

from bot.dao import UserDAO
from bot.models import User
from dao.database import async_session_maker

class CheckIsAdmin(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        async with async_session_maker() as session:
            admins_ids = [user.telegram_id for user in await UserDAO.get_admins(session)]
            if event.from_user.id in admins_ids:
                return await handler(event, data) 
            else:
                await event.answer(
                    "Только администраторы могут пользоваться этим функционалом"
                )

from dao.base import BaseDAO
from bot.models import User
from bot.schemas import UserFilterModel
from sqlalchemy.ext.asyncio import AsyncSession


class UserDAO(BaseDAO[User]):
    model = User
    async def get_all_users(session:AsyncSession) -> list[User]|None:
        """
        Получает список всех пользователей, помимо администрации
        """
        filters = UserFilterModel(role=User.Role.User)
        return await UserDAO.find_all(session, filters=filters)

    async def get_banned_users(session: AsyncSession) -> list[User]|None:
        """
        Получает список всех заблокированных пользователей.
        """
        filters = UserFilterModel(verification_code=User.VerificationCode.Blocked)
        return await UserDAO.find_all(session, filters=filters)
    
    async def get_admins(session:AsyncSession) -> list[User]|None:
        """
        Получает список всех администраторов.
        """
        filters = UserFilterModel(role=User.Role.Admin)
        return await UserDAO.find_all(session, filters=filters)
    
    async def find_by_telegram_id(session:AsyncSession,telegram_id:int) -> User|None:
        """
        Получает юзера по его телграмм id
        """
        filters = UserFilterModel(telegram_id=telegram_id)
        return await UserDAO.find_one_or_none(session,filters=filters)
from pydantic import BaseModel, ConfigDict
from typing import Optional
from bot.models import User

class TelegramIDModel(BaseModel):
    telegram_id: int

    model_config = ConfigDict(from_attributes=True)

class UserModel(TelegramIDModel):
    """
    Schemas to create user
    """
    username: str | None
    first_name: str | None
    last_name: str | None
    role: User.Role = User.Role.User

class UserFilterModel(BaseModel):
    """
    Schemas to find user
    """
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[User.Role] = None

    class Config:
        from_attributes = True
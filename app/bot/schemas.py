from pydantic import BaseModel, ConfigDict
from typing import Optional
from bot.models import User

class TelegramIDModel(BaseModel):
    telegram_id: int
    class Config:
        from_attributes = True

class UserModel(TelegramIDModel):
    """
    Schemas to create user
    """
    username: str 
    first_name: str
    last_name: str 
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

class ProjectModel(BaseModel):
    name:str
    description_small: str
    description_large:str
    telegram_bot_url: str
    developers: str
    github_link: str
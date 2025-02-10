from pydantic import BaseModel, ConfigDict
from typing import Optional
from bot.models import User

class TelegramIDModel(BaseModel):
    telegram_id: int

    model_config = ConfigDict(from_attributes=True)

class UserModel(TelegramIDModel):
    username: str | None
    first_name: str | None
    last_name: str | None
    verification_code: User.VerificationCode = User.VerificationCode.NotVerified
    role: User.Role = User.Role.User

class UserFilterModel(BaseModel):
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    verification_code: Optional[User.VerificationCode] = None
    role: Optional[User.Role] = None

    class Config:
        from_attributes = True
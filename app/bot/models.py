import enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger,Enum

from typing import Optional
from dao.database import Base

class User(Base):
    class Role(enum.Enum):
        Admin = "Admin"
        User = "User"
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[Optional[str]]
    first_name: Mapped[Optional[str]]
    last_name: Mapped[Optional[str]]
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.User)

class Project(Base):
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    description_small: Mapped[Optional[str]]
    description_large: Mapped[Optional[str]]
    telegram_bot_url: Mapped[Optional[str]]
    developers: Mapped[str]
    rating: Mapped[Optional[float]]
    github_link: Mapped[Optional[str]]
    
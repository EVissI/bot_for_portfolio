﻿import enum
from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy import BigInteger,Enum, ForeignKey

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
    description_small: Mapped[str]
    description_large: Mapped[str]
    telegram_bot_url: Mapped[str]
    developers: Mapped[str]
    github_link: Mapped[Optional[str]]
    rating: Mapped[list["ProjectRating"]] = relationship(back_populates="projecs")

class ProjectRating(Base):
    rating: Mapped[int]
    project_name: Mapped[str] = mapped_column(BigInteger, ForeignKey('projects.name'))
    project: Mapped['Project'] = relationship(back_populates="projectratings")

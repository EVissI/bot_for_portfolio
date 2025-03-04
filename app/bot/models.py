﻿import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Enum, Float, ForeignKey, String, Boolean
from typing import Optional
from app.dao.database import Base


class User(Base):
    class Role(enum.Enum):
        Admin = "Admin"
        User = "User"

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[Optional[str]]
    first_name: Mapped[Optional[str]]
    last_name: Mapped[Optional[str]]
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.User)

    project_ratings: Mapped[list["ProjectRating"]] = relationship(back_populates="user")

class Project(Base):
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, default=False)
    img_id: Mapped[Optional[str]] =  mapped_column(String, default=None)
    description_small: Mapped[str]
    description_large: Mapped[str]
    telegram_bot_url: Mapped[str]
    developers: Mapped[str] = mapped_column(String, default='@Ebezin')
    github_link: Mapped[Optional[str]]
    rating: Mapped[float] = mapped_column(Float, default=0)
    project_ratings: Mapped[list["ProjectRating"]] = relationship(back_populates="project")

class ProjectRating(Base):
    rating: Mapped[int]
    telegram_user_id: Mapped[str] = mapped_column(BigInteger, ForeignKey('users.telegram_id'),unique=False)
    project_name: Mapped[str] = mapped_column(String, ForeignKey('projects.name'),unique=False)

    project: Mapped['Project'] = relationship(back_populates="project_ratings")
    user: Mapped['User'] = relationship(back_populates="project_ratings")


    
import re
from typing import Any, Dict
from aiogram.dispatcher.router import Router
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandObject, CommandStart,Command

from loguru import logger

from bot.filters.is_register import IsRegisterFilter
from bot.keyboard.markup_kb import MainKeyboard
from bot.models import User,Project,ProjectRating
from bot.keyboard.inline_kb import vote_rating_kb,VoteProject
from bot.schemas import (TelegramIDModel, 
                        UserModel,
                        ProjectModel,ProjectFilterModel,ProjectNameModel,
                        ProjectRatingModel,ProjectRatingFilterModel)
from dao.database import connection
from bot.dao import UserDAO, ProjectDAO,ProjectRatingDAO

from config import settings

from . import start_message, contact_message,vote_responses

user_router = Router()

@user_router.message(CommandStart())
@connection()
async def cmd_start(message: Message, session, **kwargs):
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


@user_router.message(F.text == MainKeyboard.get_user_kb_texts().get("contacts"))
async def cmd_contact(message: Message):
    try:
        await message.answer(contact_message)
    except Exception as e:
        logger.error(f"Ошибка при выполнении команды контактов для пользователя {message.from_user.id}: {e}")
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова позже.")


@user_router.message(Command(re.compile(r"project_(\w+)")), IsRegisterFilter())
@connection()
async def cmd_full_info_project(message: Message, command: CommandObject, user_info: User, session, **kwargs):
    try:
        project_name: str = command.command.replace('project_','')
        project: Project = await ProjectDAO.find_one_or_none(session, ProjectNameModel(name=project_name))
        if project:
            msg = '\n'.join(
                [
                    f'💼 <b>Проект</b>: {project.name}',
                    f'👨‍💻 <b>Разработчик(и)</b>: {project.developers}',
                    f'📝 <b>Описание</b>: {project.description_large}',
                    f'🤖 <b>Ссылка на бота</b>: {project.telegram_bot_url}',
                    f'🔗 <b>Ссылка на исходный код</b>: <a href = "{project.github_link}">{project.github_link}</a>',
                    f'⭐ <b>Оценка</b>: {project.rating}',
                    '\n',
                    'Мне очень важно ваше мнение, пожалуйста оцените проект:'
                ]
            )
            await message.answer(msg, reply_markup=vote_rating_kb(project_name, user_info.telegram_id))
            return
        await message.answer('Такого проекта у меня нет ☹')
    except Exception as e:
        logger.error(f"Ошибка при выполнении команды информации о проекте для пользователя {message.from_user.id}: {e}")
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова позже.")


@user_router.callback_query(VoteProject.filter(), IsRegisterFilter())
@connection()
async def vote_project(query: CallbackQuery, callback_data: VoteProject, user_info: User, session, **kwargs):
    try:
        is_voted = await ProjectRatingDAO.find_one_or_none(
            session,
            ProjectRatingFilterModel(
                telegram_user_id=callback_data.telegram_id,
                project_name=callback_data.project_name
            )
        )

        rating_model = ProjectRatingModel(
            rating=callback_data.vote,
            telegram_user_id=callback_data.telegram_id,
            project_name=callback_data.project_name
        )

        if is_voted:
            await ProjectRatingDAO.update(
                session,
                ProjectRatingFilterModel(
                    telegram_user_id=callback_data.telegram_id,
                    project_name=callback_data.project_name
                ),
                rating_model
            )
        else:
            await ProjectRatingDAO.add(session, rating_model)
        await query.answer(vote_responses.get(callback_data.vote, "Спасибо за ваш отзыв!"))

        all_votes = await ProjectRatingDAO.find_all(session, ProjectRatingFilterModel(project_name=callback_data.project_name))
        new_rating = sum(rating.rating for rating in all_votes) / len(all_votes)
        project: Project = await ProjectDAO.find_one_or_none(session, ProjectNameModel(name=callback_data.project_name))
        await ProjectDAO.update(session,
                                ProjectNameModel(name=callback_data.project_name),
                                ProjectModel(
                                    name=project.name,
                                    description_small=project.description_small,
                                    description_large=project.description_small,
                                    telegram_bot_url=project.telegram_bot_url,
                                    github_link=project.github_link,
                                    rating=new_rating
                                ))

        pattern = r"(<b>Оценка</b>:\s*)\d+(\.\d+)?"
        new_text = re.sub(pattern, f'<b>Оценка</b>: {str(new_rating)}', query.message.html_text)
        await query.message.edit_text(new_text, reply_markup=query.message.reply_markup)
    except Exception as e:
        logger.error('Ошибка при попытке оценивания:' + str(e))
        await query.answer('Чет пошло не так')


@user_router.message(F.text == MainKeyboard.get_user_kb_texts().get("my_projects"), IsRegisterFilter())
@connection()
async def cmd_my_projects(message: Message, user_info: User, session, **kwargs):
    try:
        projects = await ProjectDAO.find_all(
            session, ProjectFilterModel()
        )
        logger.info(projects)
        msg = ''
        if projects:
            for project in projects:
                msg += '\n'.join(
                    [
                        '\n*-----------*',
                        f'💼Проект: {project.name}',
                        f'📝Описание проекта: {project.description_small}',
                        f'⭐Оценка: <b>{project.rating}</b>',
                        f'Подробная информация - /project_{project.name}',
                        '*-------------*'
                    ]
                )
        else:
            msg = 'Тут пока пусто:('
        await message.answer(
            msg,
            reply_markup=MainKeyboard.build(user_info.role),
        )
    except Exception as e:
        logger.error(f"Ошибка при выполнении команды моих проектов для пользователя {message.from_user.id}: {e}")
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова позже.")


@user_router.message(IsRegisterFilter())
async def cmd_unknow(message: Message, user_info: User):
    try:
        await message.answer(
            "Я не знаю такой команды, пользуетесь только клавиатурой",
            reply_markup=MainKeyboard.build(user_info.role),
        )
    except Exception as e:
        logger.error(f"Ошибка при выполнении неизвестной команды для пользователя {message.from_user.id}: {e}")
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова позже.")

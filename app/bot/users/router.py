import re

from aiogram import F,Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandObject, CommandStart,Command

from loguru import logger

from app.bot.filters.is_register import IsRegisterFilter
from app.bot.keyboard.markup_kb import MainKeyboard
from app.bot.models import User,Project,ProjectRating
from app.bot.keyboard.inline_kb import vote_rating_kb,VoteProject
from app.bot.schemas import (TelegramIDModel, 
                        UserModel,
                        ProjectModel,ProjectFilterModel,ProjectNameModel,
                        ProjectRatingModel,ProjectRatingFilterModel)
from app.dao.database import connection, async_session_maker
from app.bot.dao import UserDAO, ProjectDAO,ProjectRatingDAO

from app.config import settings,bot

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
            await message.answer(msg, reply_markup=MainKeyboard.build_main_kb(user_info.role))
            return
        if user_id in settings.ROOT_ADMIN_IDS:
            values = UserModel(
                telegram_id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                role=User.Role.Admin,
            )
            await UserDAO.add(session=session, values=values)
            await message.answer(
                "Привет администрации", reply_markup=MainKeyboard.build_main_kb(User.Role.Admin)
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
        await message.answer(msg, reply_markup=MainKeyboard.build_main_kb(User.Role.User))
        for admin in settings.ROOT_ADMIN_IDS:
            await bot.send_message(admin,f'К тебе зашел новый юзер {message.from_user.first_name} [id: {message.from_user.id}]')
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
                    f'🔗 <b>Ссылка на исходный код</b>: <a href = "{project.github_link}">{project.github_link}</a>' if project.github_link else '',
                    f'⭐ <b>Оценка</b>: {project.rating}',
                    '\n',
                    'Мне очень важно ваше мнение, пожалуйста оцените проект:'
                ]
            )
            if project.img_id:
                await message.answer_photo(project.img_id,caption=msg,reply_markup=vote_rating_kb(project_name, user_info.telegram_id))
                return
            else:
                await message.answer(msg, reply_markup=vote_rating_kb(project_name, user_info.telegram_id))
                return
        await message.answer('Такого проекта у меня нет ☹')
    except Exception as e:
        logger.error(f"Ошибка при выполнении команды информации о проекте для пользователя {message.from_user.id}: {e}")
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова позже.")


@user_router.callback_query(VoteProject.filter(), IsRegisterFilter())
async def vote_project(query: CallbackQuery, callback_data: VoteProject, user_info: User):
    try:
        async with async_session_maker() as session:
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
        async with async_session_maker() as session:
            all_votes = await ProjectRatingDAO.find_all(session, ProjectRatingFilterModel(project_name=callback_data.project_name))
            new_rating = sum(rating.rating for rating in all_votes) / len(all_votes)
            project: Project = await ProjectDAO.find_one_or_none(session, ProjectNameModel(name=callback_data.project_name))
            project.rating = new_rating
            await ProjectDAO.update(session,
                                    ProjectNameModel(name=callback_data.project_name),
                                    ProjectModel.model_validate(project.to_dict()))

            pattern = r"(<b>Оценка</b>:\s*)\d+(\.\d+)?"
            new_text = re.sub(pattern, f'<b>Оценка</b>: {str(new_rating)}', query.message.html_text)
            if project.img_id:
                await query.message.edit_caption(caption=new_text, reply_markup=query.message.reply_markup)
            else:
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
                        '\n-----------',
                        f'💼Проект: {project.name}',
                        f'📝Описание проекта: {project.description_small}',
                        f'⭐Оценка: <b>{project.rating}</b>',
                        f'Подробная информация - /project_{project.name}',
                        '-------------'
                    ]
                )
        else:
            msg = 'Тут пока пусто:('
        await message.answer(
            msg,
            reply_markup=MainKeyboard.build_main_kb(user_info.role),
        )
    except Exception as e:
        logger.error(f"Ошибка при выполнении команды моих проектов для пользователя {message.from_user.id}: {e}")
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова позже.")


@user_router.message(IsRegisterFilter())
async def cmd_unknow(message: Message, user_info: User):
    try:
        await message.answer(
            "Я не знаю такой команды, пользуетесь только клавиатурой",
            reply_markup=MainKeyboard.build_main_kb(user_info.role),
        )
    except Exception as e:
        logger.error(f"Ошибка при выполнении неизвестной команды для пользователя {message.from_user.id}: {e}")
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова позже.")

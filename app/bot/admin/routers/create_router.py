import re
from aiogram import Router, F
from aiogram.types import Message,CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackData

from loguru import logger
from bot.schemas import ProjectModel
from bot.dao import ProjectDAO
from bot.models import User
from bot.keyboard.inline_kb import confirm_kb,AdminCallback
from bot.keyboard.markup_kb import skip_button,main_keyboard
from dao.database import connection

admin_router_create_project = Router()
class AddProject(StatesGroup):
    name = State()
    developers = State()
    small_deskript = State()
    large_deskript = State()
    telegram_bot_link = State()
    github_link = State()
    confirm = State()


state_dict = {
    "name": "имя",
    "developers":"телеграмм тег создателя проекта или телеграмм теги участвующих в проекте через запятую",
    "small_deskript": "краткое описание проекта",
    "large_deskript": "полное описание проекта",
    "telegram_bot_link": "ссылку на бота или его тег через @",
    "github_link": "ссылку на репозиторий",
}

@admin_router_create_project.message(F.text == "Добавить проект")
async def add_new_project(message: Message, state: FSMContext):
    await state.set_state(AddProject.name)
    await message.answer("Введите название проекта:", reply_markup=skip_button())


async def process_project_data(
    message: Message, state: FSMContext, field_name: str, next_state: State
):
    if message.text.lower() == "отменить создание":
        await state.clear()
        await message.answer(
            f"Окей отменяю", reply_markup=main_keyboard(User.Role.Admin)
        )
    else:
        await state.update_data({field_name: message.text})
        await state.set_state(next_state)
        await message.answer(
            f"Введите {state_dict.get(next_state._state)}: ", reply_markup=skip_button()
        )

@admin_router_create_project.message(StateFilter(AddProject.name))
async def process_name(message: Message, state: FSMContext):
    await process_project_data(message, state, "name", AddProject.developers)

@admin_router_create_project.message(StateFilter(AddProject.developers))
async def process_developer(message: Message, state: FSMContext):
    await process_project_data(message, state, "developers", AddProject.small_deskript)

@admin_router_create_project.message(StateFilter(AddProject.small_deskript))
async def process_small_deskript(message: Message, state: FSMContext):
    await process_project_data(
        message, state, "small_deskript", AddProject.large_deskript
    )


@admin_router_create_project.message(StateFilter(AddProject.large_deskript))
async def process_large_deskript(message: Message, state: FSMContext):
    await process_project_data(
        message, state, "large_deskript", AddProject.telegram_bot_link
    )


telegram_bot_link_pattern = re.compile(r"^(https://t.me/[\w_]+|@[A-Za-z0-9_]+)$")


@admin_router_create_project.message(
    F.text.lower() == "отменить создание" or F.text.regexp(telegram_bot_link_pattern),
    StateFilter(AddProject.telegram_bot_link),
)
async def process_telegram_bot_link(message: Message, state: FSMContext):
    await process_project_data(
        message, state, "telegram_bot_link", AddProject.github_link
    )


@admin_router_create_project.message(
    ~F.text.regexp(telegram_bot_link_pattern), StateFilter(AddProject.telegram_bot_link)
)
async def un_process_telegram_bot_link(message: Message, state: FSMContext):
    await message.answer("Это не похоже на телеговскую ссылку")
    await process_project_data(
        message, state, "large_deskript", AddProject.telegram_bot_link
    )


https_link_pattern = re.compile(r"^https://.*")


async def get_data(state):
    data = await state.get_data()
    name, developers, small_deskript, large_deskript, telegram_bot_link, github_link = (
        data.get('name'),
        data.get('developers'),
        data.get('small_deskript'),
        data.get('large_deskript'),
        data.get('telegram_bot_link'),
        data.get('github_link'),
    )
    
    return name,developers,small_deskript,large_deskript,telegram_bot_link,github_link

@admin_router_create_project.message(
    F.text.lower() == "отменить создание" or F.text.regexp(https_link_pattern),
    StateFilter(AddProject.github_link),
)
async def process_github_link(message: Message, state: FSMContext):
    if message.text.lower() == "отменить создание":
        await state.clear()
        await message.answer(
            f"Окей отменяю", reply_markup=main_keyboard(User.Role.Admin)
        )
    else:
        state.update_data({"github_link": message.text})
    await state.set_state(AddProject.confirm)
    name, developers, small_deskript, large_deskript, telegram_bot_link, github_link = await get_data(state)

    msg = (
    f"Имя проекта: {name}\n" if name else "" +
    f"Создатель(и): {developers}\n" if name else "" +
    f"Краткое описание проекта: {small_deskript}\n" if small_deskript else "" +
    f"Полное описание проекта: {large_deskript}\n" if large_deskript else "" +
    f"Ссылка на бота: {telegram_bot_link}\n" if telegram_bot_link else "" +
    f"Ссылка на репозиторий: {github_link}\n" if github_link else ""
    )

    await message.answer(msg + "\nПодтвердите публикацию",reply_markup=confirm_kb())


@admin_router_create_project.message(
    ~F.text.regexp(https_link_pattern), StateFilter(AddProject.github_link)
)
async def un_process_github_link(message: Message, state: FSMContext):
    await message.answer("Это не похоже на ссылку")
    await process_project_data(
        message, state, "telegram_bot_link", AddProject.github_link
    )

@admin_router_create_project.callback_query(AdminCallback.filter())
@connection()
async def process_confirm(query: CallbackQuery, callback_data: AdminCallback,state:FSMContext, session, **kwargs):
    if callback_data.action == "admin_confirm_project_yes":
        name,developers, small_deskript, large_deskript, telegram_bot_link, github_link = await get_data(state)
        values = ProjectModel(
            name=name,
            description_small=small_deskript,
            description_large=large_deskript,
            telegram_bot_url=telegram_bot_link,
            developers=developers,
            github_link=github_link
        )
        
    elif callback_data.action == "admin_confirm_project_no":
        await query.message.answer('Понял, отменяю публикацию',reply_markup=main_keyboard(User.Role.Admin))
        await state.clear()

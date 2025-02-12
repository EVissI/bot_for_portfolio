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
from bot.keyboard.markup_kb import cancel_button,main_keyboard
from dao.database import connection

admin_router_create_project = Router()
class AddProject(StatesGroup):
    name = State()
    small_deskript = State()
    large_deskript = State()
    telegram_bot_link = State()
    github_link = State()
    confirm = State()


state_dict = {
    "name": "имя",
    "small_deskript": "краткое описание проекта",
    "large_deskript": "полное описание проекта",
    "telegram_bot_link": "ссылку на бота или его тег через @",
    "github_link": "ссылку на репозиторий",
}

@admin_router_create_project.message(F.text == "Добавить проект")
async def add_new_project(message: Message, state: FSMContext):
    await state.set_state(AddProject.name)
    await message.answer("Введите название проекта:", reply_markup=cancel_button())


async def process_project_data(
    message: Message, state: FSMContext, field_name: str, next_state: State
):
    if message.text.lower() == "отменить создание":
        await state.clear()
        await message.answer(
            f"Окей, отменяю", reply_markup=main_keyboard(User.Role.Admin)
        )
    else:
        await state.update_data({field_name: message.text})
        await state.set_state(next_state)
        await message.answer(
            f"Введите {state_dict.get(next_state._state)}: ", reply_markup=cancel_button()
        )

@admin_router_create_project.message(StateFilter(AddProject.name))
async def process_name(message: Message, state: FSMContext):
    await process_project_data(message, state, "name", AddProject.small_deskript)


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


telegram_bot_link_pattern = r"^(@[A-Za-z0-9_]{5,32}bot)$"

@admin_router_create_project.message(F.text.lower() == "отменить создание")
@admin_router_create_project.message(
    F.text.regexp(telegram_bot_link_pattern),
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
    await message.answer("Это не похоже на телеговскую ссылку на бота, она должна начинаться на @ и заканчиваться bot")
    await process_project_data(
        message, state, "large_deskript", AddProject.telegram_bot_link
    )


https_link_pattern = r"^https://.*"


@admin_router_create_project.message(F.text.lower() == "отменить создание")
@admin_router_create_project.message(
    F.text.regexp(https_link_pattern),
    StateFilter(AddProject.github_link),
)
async def process_github_link(message: Message, state: FSMContext):
    if message.text.lower() == "отменить создание":
        await state.clear()
        await message.answer(
            f"Окей, отменяю", reply_markup=main_keyboard(User.Role.Admin)
        )
        return
    
    await state.update_data({"github_link": message.text})

    data = await state.get_data()
    logger.info(data)
    msg = "\n".join(
    [
        f"<b>Имя проекта</b>: {data.get('name')}" if data.get('name') else "",
        f"<b>Краткое описание проекта</b>: {data.get('small_deskript')}" if data.get('small_deskript') else "",
        f"<b>Полное описание проекта</b>: {data.get('large_deskript')}" if data.get('large_deskript') else "",
        f"<b>Ссылка на бота</b>: {data.get('telegram_bot_link')}" if data.get('telegram_bot_link') else "",
        f"<b>Ссылка на репозиторий</b>: {data.get('github_link')}" if data.get('github_link') else ""
    ]
    )
    msg = msg.strip()


    await message.answer(msg + "\nПодтвердите публикацию",reply_markup=confirm_kb(data['name']))
    await state.set_state(AddProject.confirm)

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
    logger.info(callback_data.action)
    if callback_data.action == "yes":
        data = await state.get_data()
        values = ProjectModel(
            name=data.get("name"),
            description_small=data.get("small_deskript"),
            description_large=data.get("large_deskript"),
            telegram_bot_url=data.get("telegram_bot_link"),
            github_link=data.get("github_link")
        )
        await ProjectDAO.add(session,values)
        await query.message.delete()
        await query.message.answer('Добавление прошло успешно', reply_markup=main_keyboard(User.Role.Admin))
        await state.clear()
    elif callback_data.action == "no":
        await query.message.delete()
        await query.message.answer('Понял, отменяю публикацию',reply_markup=main_keyboard(User.Role.Admin))
        await state.clear()

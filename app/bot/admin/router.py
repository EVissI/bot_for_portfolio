import re
from aiogram import Router,F
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from bot.keyboard.markup_kb import skip_button
from dao.database import connection


admin_router = Router()

class AddProject(StatesGroup):
    name = State()
    small_deskript = State()
    large_deskript = State()
    telegram_bot_link = State()
    github_link = State()

state_dict = {
    "name": "имя",
    "small_deskript": "краткое описание проекта",
    "large_deskript": "полное описание проекта",
    "telegram_bot_link": "ссылку на бота или его тег через @",
    "github_link": "ссылку на репозиторий",
}


@admin_router.message(F.text == "Добавить проект")
async def add_new_project(message:Message,state:FSMContext):
    await state.set_state(AddProject.name)
    await message.answer("Введите название проекта:", reply_markup=skip_button())


async def process_project_data(message: Message, state: FSMContext, field_name: str, next_state: State):
    if message.text.lower() == "пропустить":
        await state.update_data({field_name: None})  
        await state.set_state(next_state)
        await message.answer(f"Введите {state_dict.get(next_state)}: ", reply_markup=skip_button())
    else:
        await state.update_data({field_name: message.text})
        await state.set_state(next_state)
        await message.answer(f"Введите {state_dict.get(next_state)}: ", reply_markup=skip_button())

@admin_router.message_handler(StateFilter(AddProject.name))
async def process_name(message: Message, state: FSMContext):
    await process_project_data(message, state, "name", AddProject.small_deskript)

@admin_router.message_handler(StateFilter(AddProject.small_deskript))
async def process_small_deskript(message: Message, state: FSMContext):
    await process_project_data(message, state, "small_deskript", AddProject.large_deskript)

@admin_router.message_handler(StateFilter(AddProject.large_deskript))
async def process_large_deskript(message: Message, state: FSMContext):
    await process_project_data(message, state, "large_deskript", AddProject.telegram_bot_link)

telegram_bot_link_pattern = re.compile(r'^(https://t.me/[\w_]+|@[A-Za-z0-9_]+)$')
@admin_router.message_handler(F.text.regexp(telegram_bot_link_pattern),StateFilter(AddProject.telegram_bot_link))
async def process_telegram_bot_link(message: Message, state: FSMContext):
    await process_project_data(message, state, "telegram_bot_link", AddProject.github_link)

@admin_router.message_handler(~F.text.regexp(telegram_bot_link_pattern),StateFilter(AddProject.telegram_bot_link))
async def un_process_telegram_bot_link(message: Message, state: FSMContext):
    await message.answer('Это не похоже на телеговскую ссылку')
    await process_project_data(message, state, "large_deskript", AddProject.telegram_bot_link)

https_link_pattern = re.compile(r'^https://.*')

@admin_router.message_handler(~F.text.regexp(https_link_pattern),StateFilter(AddProject.github_link))
async def un_process_github_link(message: Message, state: FSMContext):
    await message.answer('Это не похоже на ссылку')
    await process_project_data(message, state, "telegram_bot_link", AddProject.github_link)

@admin_router.message_handler(F.text.regexp(https_link_pattern),StateFilter(AddProject.github_link))
@connection()
async def process_github_link(message: Message, state: FSMContext, session,**kwargs):
    if message.text.lower() == "пропустить":
        await state.update_data({"github_link": None}) 
    else:
        state.update_data({"github_link": message.text})
    await state.clear()
    await message.answer("Проект добавлен!")
import re
from aiogram import Router, F
from aiogram.types import Message,CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from loguru import logger
from bot.admin.common import add_project_final_msg
from bot.schemas import ProjectModel,ProjectNameModel
from bot.dao import ProjectDAO
from bot.models import User
from bot.keyboard.inline_kb import confirm_kb,change_kb, AdminCallbackAddProject, AdminCallbackAddProjectChange
from bot.keyboard.markup_kb import cancel_button,main_keyboard,admin_kb_texts_dict
from dao.database import connection

admin_router_create_project = Router()
class AddProject(StatesGroup):
    name = State()
    small_deskript = State()
    large_deskript = State()
    telegram_bot_link = State()
    github_link = State()
    confirm = State()
    change = State()


@admin_router_create_project.message(F.text == admin_kb_texts_dict.get('add_project'))
async def add_new_project(message: Message, state: FSMContext):
    await state.set_state(AddProject.name)
    await message.answer("Введите название проекта:", reply_markup=cancel_button())


@admin_router_create_project.message(StateFilter(AdminCallbackAddProject) and F.text.lower() == "отменить создание" )
async def cancel_dialog(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Окей, отменяю", reply_markup=main_keyboard(User.Role.Admin)
    )


@admin_router_create_project.message(StateFilter(AddProject.name))
@connection()
async def process_name(message: Message, state: FSMContext,session,**kwargs):
    project = await ProjectDAO.find_one_or_none(session=session,
                                                filters=ProjectNameModel(name=message.text))
    if project:
        await message.answer('Проект с таким названием уже существует, попробуйте снова')
        return
    await state.update_data({"name": message.text})
    await state.set_state(AddProject.small_deskript)
    await message.answer(
        f"Введите краткое описание проекта", reply_markup=cancel_button()
    )


@admin_router_create_project.message(StateFilter(AddProject.small_deskript))
async def process_small_deskript(message: Message, state: FSMContext):
    await state.update_data({"small_deskript": message.text})
    await state.set_state(AddProject.large_deskript)
    await message.answer(
        f"Введите полное описание проекта", reply_markup=cancel_button()
    )


@admin_router_create_project.message(StateFilter(AddProject.large_deskript))
async def process_large_deskript(message: Message, state: FSMContext):
    await state.update_data({"large_deskript": message.text})
    await state.set_state(AddProject.telegram_bot_link)
    await message.answer(
        f"Введите тег бота", reply_markup=cancel_button()
    )


telegram_bot_link_pattern = r"^(@[A-Za-z0-9_]{5,32}bot)$"
@admin_router_create_project.message(
    F.text.regexp(telegram_bot_link_pattern),
    StateFilter(AddProject.telegram_bot_link),
)
async def process_telegram_bot_link(message: Message, state: FSMContext):
    await state.update_data({"telegram_bot_link": message.text})
    await state.set_state(AddProject.github_link)
    await message.answer(
        f"Введите ссылку на проект", reply_markup=cancel_button()
    )


@admin_router_create_project.message(
    ~F.text.regexp(telegram_bot_link_pattern), StateFilter(AddProject.telegram_bot_link)
)
async def warning_telegram_bot_link(message: Message, state: FSMContext):
    await message.answer("Это не похоже на телеговскую ссылку на бота, она должна начинаться на @ и заканчиваться bot\nпопробуйте снова")

https_link_pattern = r"^https://.*"
@admin_router_create_project.message(
    F.text.regexp(https_link_pattern),
    StateFilter(AddProject.github_link),
)
async def process_github_link(message: Message, state: FSMContext):   
    await state.update_data({"github_link": message.text})

    data = await state.get_data()
    logger.info(data)
    msg = await add_project_final_msg(data)
    await message.answer(msg + "\n\nПодтвердите публикацию",reply_markup=confirm_kb())
    await state.set_state(AddProject.confirm)

@admin_router_create_project.message(
    ~F.text.regexp(https_link_pattern), StateFilter(AddProject.github_link)
)
async def warning_github_link(message: Message, state: FSMContext):
    await message.answer("Это не похоже на ссылку, попробуйте снова")

@admin_router_create_project.callback_query(AdminCallbackAddProject.filter())
@connection()
async def process_confirm(query: CallbackQuery, callback_data: AdminCallbackAddProject,state:FSMContext, session, **kwargs):
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
    elif callback_data.action == 'change':
        await query.message.edit_text(query.message.text.replace("\n\nПодтвердите публикацию","\n\nВыберите что нужно поменять:"), reply_markup=change_kb())
        await state.set_state(AddProject.change)

@admin_router_create_project.callback_query(AdminCallbackAddProjectChange.filter())
async def process_change_qr(query: CallbackQuery, callback_data: AdminCallbackAddProject,state:FSMContext):
    await query.message.delete()
    await query.message.answer('Теперь введите заменяющее значение',reply_markup=cancel_button())
    await state.update_data({'changed_state':callback_data.action})

@admin_router_create_project.message(AddProject.change)
async def process_change_msg(message:Message, state:FSMContext):
    data = await state.get_data()
    match data['changed_state']:
        case 'small_deskript':
            await state.update_data({'small_deskript':message.text})
        case 'large_deskript':
            await state.update_data({'large_deskript':message.text})
        case 'telegram_bot_link':
            if re.match(telegram_bot_link_pattern, message.text):
                await state.update_data({'telegram_bot_link': message.text})
            else:
                await message.answer("Это не похоже на телеговскую ссылку на бота, она должна начинаться на @ и заканчиваться bot\nпопробуйте снова")
                return
        case 'github_link':
            if re.match(https_link_pattern, message.text):
                await state.update_data({'github_link': message.text})
            else:
                await message.answer("Это не похоже на ссылку, попробуйте снова")
                return
    await state.set_state(AddProject.confirm)
    data = await state.get_data()
    msg = await add_project_final_msg(data)
    await message.answer(msg + "\n\nПодтвердите публикацию",reply_markup=confirm_kb())
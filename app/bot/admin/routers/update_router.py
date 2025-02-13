import re
from aiogram import Router,F
from aiogram.types import Message,CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from loguru import logger

from bot.keyboard.inline_kb import update_kb,AdminCallbackProjectUpdate
from bot.admin.common import add_project_final_msg
from bot.models import User
from bot.dao import ProjectDAO
from bot.schemas import ProjectNameModel,ProjectModel
from dao.database import connection
from bot.keyboard.markup_kb import CancelButton, MainKeyboard
from bot.admin.common import https_link_pattern,telegram_bot_url_pattern


update_project = Router()

class UpdateProject(StatesGroup):
    name = State()
    update = State()
    take_data_to_update = State()

@update_project.message(F.text == MainKeyboard.get_admin_kb_texts().get('change_project'))
async def cmd_change_project(message:Message,state:FSMContext):
    await message.answer('Введите название проекта для изменения',reply_markup=CancelButton.build('update'))
    await state.set_state(UpdateProject.name)


@update_project.message(StateFilter(UpdateProject) and F.text == CancelButton.get_cancel_texts().get('update') )
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Ок,возвращаю в главное меню", reply_markup=MainKeyboard.build(User.Role.Admin)
    )

@update_project.message(StateFilter(UpdateProject.name), F.text)
@connection()
async def find_project_by_name(message:Message,state:FSMContext,session,**kwargs):
    project_info = await ProjectDAO.find_one_or_none(
        session=session, filters=ProjectNameModel(name=message.text)
    )
    if not project_info:
        await message.answer(
            "Ничего не нашел, попробуй еще раз",
            reply_markup=CancelButton.build('update'),
        )
        return
    msg = await add_project_final_msg(project_info.to_dict())
    await state.set_data(project_info.to_dict())
    await message.answer(msg + '\n\n <b>Выберите что нужно изменить:</b>',reply_markup=update_kb())
    await state.set_state(UpdateProject.update)

@update_project.callback_query(AdminCallbackProjectUpdate.filter())
@connection()
async def process_update_project_qr(query: CallbackQuery, callback_data: AdminCallbackProjectUpdate,state:FSMContext,session,**kwargs):
    data = await state.get_data()
    match callback_data.action:
        case 'save':
            project_info = (await ProjectDAO.find_one_or_none(
                session=session, filters=ProjectNameModel(name=data.get('name'))
            )).to_dict()
            project_info.update(data)
            project_info = ProjectModel.model_validate(project_info)
            await ProjectDAO.update(session=session,filters=ProjectNameModel(name=data.get('name')),values = project_info)
            await query.message.delete()
            await query.message.answer('Данные обновленны',reply_markup=MainKeyboard.build(User.Role.Admin))
            await state.clear()
        case _:
            await query.message.delete()
            await state.update_data({'update_data':callback_data.action})
            await state.set_state(UpdateProject.take_data_to_update)
            await query.message.answer('Введите новые данные', reply_markup=CancelButton.build('update'))

@update_project.message(StateFilter(UpdateProject.take_data_to_update))
async def process_update_project_msg(message:Message,state:FSMContext):
    data = await state.get_data()
    logger.info(data)
    match data['update_data']:
        case 'telegram_bot_url':
            if re.match(telegram_bot_url_pattern, message.text):
                await state.update_data({'telegram_bot_url': message.text})
            else:
                await message.answer("Это не похоже на телеговскую ссылку на бота, она должна начинаться на @ и заканчиваться bot\nпопробуйте снова")
                return
        case 'github_link':
            if re.match(https_link_pattern, message.text):
                await state.update_data({'github_link': message.text})
            else:
                await message.answer("Это не похоже на ссылку, попробуйте снова")
                return
        case _:
            await state.update_data({data['update_data']:message.text})
    await state.set_state(UpdateProject.update)
    data = await state.get_data()
    logger.info(data)
    msg = await add_project_final_msg(data)
    await message.answer(msg + '\n\n <b>Выберите что нужно изменить:</b>',reply_markup=update_kb())
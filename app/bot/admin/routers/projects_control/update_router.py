import re
from aiogram import Router,F
from aiogram.types import Message,CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from loguru import logger

from bot.admin.states import AdminPanelStates, UpdateProject
from bot.keyboard.inline_kb import ProjectList, project_list_kb, update_kb,AdminCallbackProjectUpdate
from bot.admin.common import add_project_final_msg
from bot.dao import ProjectDAO
from bot.schemas import ProjectNameModel,ProjectModel,ProjectFilterModel
from dao.database import connection
from bot.keyboard.markup_kb import CancelButton, MainKeyboard
from bot.admin.common import https_link_pattern,telegram_bot_url_pattern


update_project = Router()



@update_project.message(F.text == MainKeyboard.get_project_contol_kb().get('change_project'),StateFilter(AdminPanelStates.project_control))
@connection()
async def cmd_change_project(message:Message,state:FSMContext,session,**kwargs):
    projects = await ProjectDAO.find_all(session,ProjectFilterModel())
    projects_list = []
    for project in projects:
        projects_list.append(project.name)
    await message.answer('Выбери проект который нужно изменить:',reply_markup=project_list_kb(projects_list,'update'))

@update_project.callback_query(ProjectList.filter(F.action == 'update'))
@connection()
async def process_project_name(query: CallbackQuery, callback_data: ProjectList,state:FSMContext,session,**kwargs):
    if callback_data.name is not None and not callback_data.is_empety:
        project_info = await ProjectDAO.find_one_or_none(
        session=session, filters=ProjectNameModel(name=callback_data.name)
        )
        msg = await add_project_final_msg(project_info.to_dict())
        await query.message.delete()
        await state.set_data(project_info.to_dict())
        await query.message.answer(msg + '\n\n <b>Выберите что нужно изменить:</b>',reply_markup=update_kb())
        await state.set_state(UpdateProject.update)
        return
    elif callback_data.name is None and not callback_data.is_empety:
        projects = await ProjectDAO.find_all(session,ProjectFilterModel())
        projects_list = []
        for project in projects:
            projects_list.append(project.name)
        await query.message.edit_reply_markup(reply_markup = project_list_kb(projects_list,'update',page=callback_data.page))
    elif callback_data.is_empety:
        await query.answer('Ты зачем сюда жмакаешь?')


    
@update_project.message(StateFilter(UpdateProject) and F.text == CancelButton.get_cancel_texts().get('update') )
async def cmd_cancel(message: Message, state: FSMContext):
    await state.set_state(AdminPanelStates.project_control)
    await message.answer(
        f"Ок,возвращаю в главное меню", reply_markup= MainKeyboard.build_project_cotrol_panel()
    )


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
            await query.message.answer('Данные обновленны',reply_markup=MainKeyboard.build_project_cotrol_panel())
            await state.set_state(AdminPanelStates.project_control)
        case _:
            await query.message.delete()
            await state.update_data({'update_data':callback_data.action})
            await state.set_state(UpdateProject.take_data_to_update)
            await query.message.answer('Введите новые данные', reply_markup=CancelButton.build('update'))

@update_project.message(StateFilter(UpdateProject.take_data_to_update),~F.text)
async def warning_not_text(message:Message):
    await message.answer("Только текст,брача")

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
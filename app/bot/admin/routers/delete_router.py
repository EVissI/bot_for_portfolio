from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from loguru import logger

from bot.admin.common import add_project_final_msg
from bot.models import User
from bot.schemas import ProjectFilterModel, ProjectNameModel
from bot.dao import ProjectDAO
from dao.database import connection
from bot.keyboard.markup_kb import MainKeyboard, CancelButton
from bot.keyboard.inline_kb import AdminCallbackDeleteProject, ProjectList, confirm_del_kb, project_list_kb


class DeleteProject(StatesGroup):
    name = State()
    confirm = State()


delete_project = Router()


@delete_project.message(
    F.text == MainKeyboard.get_admin_kb_texts().get("delete_project")
)
@connection()
async def cmd_delete_project(message: Message, state: FSMContext,session,**kwargs):
    projects = await ProjectDAO.find_all(session,ProjectFilterModel())
    projects_list = []
    for project in projects:
        projects_list.append(project.name)
    await message.answer('Выбери проект который исстребляем:',reply_markup=project_list_kb(projects_list))


@delete_project.callback_query(ProjectList.filter())
@connection()
async def process_project_name(query: CallbackQuery, callback_data: ProjectList,state:FSMContext,session,**kwargs):
    if callback_data.name is not None:
        project_info = await ProjectDAO.find_one_or_none(
        session=session, filters=ProjectNameModel(name=callback_data.name)
        )
        msg = await add_project_final_msg(project_info.to_dict())
        await query.message.delete()
        await state.set_data(project_info.to_dict())
        await query.message.answer(
            msg + "\n\n <b>Подтвердите удаление</b>", reply_markup=confirm_del_kb()
        )
        await state.set_state(DeleteProject.confirm)
        return
    elif callback_data.name is None:
        projects = await ProjectDAO.find_all(session,ProjectFilterModel())
        projects_list = []
        for project in projects:
            projects_list.append(project.name)
        await query.message.edit_reply_markup(reply_markup = project_list_kb(projects_list,page=callback_data.page))
    elif callback_data == 'list_project_empety':
        await query.answer('Ты зачем сюда жмакаешь?')


@delete_project.message(StateFilter(DeleteProject) and F.text == CancelButton.get_cancel_texts().get("delete") )
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Ок,возвращаю в главное меню", reply_markup=MainKeyboard.build(User.Role.Admin)
    )


@delete_project.callback_query(AdminCallbackDeleteProject.filter())
@connection()
async def process_delete_project_qr(
    query: CallbackQuery, callback_data: AdminCallbackDeleteProject, state: FSMContext,session,**kwargs
):
    if callback_data.action == "yes":
        project_name = (await state.get_data()).get('name')
        logger.info(project_name)
        await ProjectDAO.delete(
            session=session, filters=ProjectNameModel(name=project_name)
        )
        await query.message.delete()
        await query.message.answer(f'Удалил проект {project_name}',reply_markup= MainKeyboard.build(User.Role.Admin))
    if callback_data.action == "no":
        await query.message.delete()
        await state.clear()
        await query.message.answer(f'Не надо, так не надо',reply_markup= MainKeyboard.build(User.Role.Admin))
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from loguru import logger

from bot.admin.common import add_project_final_msg
from bot.models import User
from bot.schemas import ProjectNameModel
from bot.dao import ProjectDAO
from dao.database import connection
from bot.keyboard.markup_kb import MainKeyboard, CancelButton
from bot.keyboard.inline_kb import AdminCallbackDeleteProject, confirm_del_kb


class DeleteProject(StatesGroup):
    name = State()
    confirm = State()


delete_project = Router()


@delete_project.message(
    F.text == MainKeyboard.get_admin_kb_texts().get("delete_project")
)
async def cmd_delete_project(message: Message, state: FSMContext):
    await message.answer(
        "Введите название проекта, который хотите удалить",
        reply_markup=CancelButton.build("delete"),
    )
    await state.set_state(DeleteProject.name)


@delete_project.message(StateFilter(DeleteProject) and F.text == CancelButton.get_cancel_texts().get("delete") )
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Ок,возвращаю в главное меню", reply_markup=MainKeyboard.build(User.Role.Admin)
    )


@delete_project.message(F.text, StateFilter(DeleteProject.name))
@connection()
async def process_delete_project_msg(
    message: Message, state: FSMContext, session, **kwargs
):
    project_info = await ProjectDAO.find_one_or_none(
        session=session, filters=ProjectNameModel(name=message.text)
    )
    if not project_info:
        await message.answer(
            "Ничего не нашел, попробуй еще раз",
            reply_markup=CancelButton.build("delete"),
        )
        return
    await state.update_data({'name':message.text})
    msg = await add_project_final_msg(project_info.to_dict())
    await message.answer(
        msg + "\n\n <b>Подтвердите удаление</b>", reply_markup=confirm_del_kb()
    )
    await state.set_state(DeleteProject.confirm)


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
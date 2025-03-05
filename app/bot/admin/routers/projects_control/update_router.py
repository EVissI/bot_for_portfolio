import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from loguru import logger

from app.bot.admin.states import AdminPanelStates, UpdateProject
from app.bot.keyboard.inline_kb import (
    ProjectList,
    project_list_kb,
    AdminCallbackProjectUpdateBaseInfo,
    AdminCallbackProjectUpdateMenu,
    update_menu,
    update_base_info_kb,
)
from app.bot.admin.common import add_project_final_msg
from app.bot.dao import ProjectDAO
from app.bot.schemas import ProjectNameModel, ProjectModel, ProjectFilterModel
from app.dao.database import connection
from app.bot.keyboard.markup_kb import CancelButton, MainKeyboard
from app.bot.admin.common import https_link_pattern


update_project = Router()


@update_project.message(
    F.text == MainKeyboard.get_project_contol_kb().get("change_project"),
    StateFilter(AdminPanelStates.project_control),
)
@connection()
async def cmd_change_project(message: Message, state: FSMContext, session, **kwargs):
    projects = await ProjectDAO.find_all(session, ProjectFilterModel())
    projects_list = []
    for project in projects:
        projects_list.append(project.name)
    await message.answer(
        "Выбери проект который нужно изменить:",
        reply_markup=project_list_kb(projects_list, "update"),
    )


@update_project.callback_query(ProjectList.filter(F.action == "update"))
@connection()
async def process_project_name(
    query: CallbackQuery,
    callback_data: ProjectList,
    state: FSMContext,
    session,
    **kwargs,
):
    if callback_data.name is not None and not callback_data.is_empety:
        project_info = await ProjectDAO.find_one_or_none(
            session=session, filters=ProjectNameModel(name=callback_data.name)
        )
        msg = await add_project_final_msg(project_info.to_dict())
        await query.message.delete()
        await state.set_data(project_info.to_dict())
        await query.message.answer(
            msg + "\n\n <b>Что делаем?:</b>", reply_markup=update_menu()
        )
        await state.set_state(UpdateProject.update_menu)
        return
    elif callback_data.name is None and not callback_data.is_empety:
        projects = await ProjectDAO.find_all(session, ProjectFilterModel())
        projects_list = []
        for project in projects:
            projects_list.append(project.name)
        await query.message.edit_reply_markup(
            reply_markup=project_list_kb(
                projects_list, "update", page=callback_data.page
            )
        )
    elif callback_data.is_empety:
        await query.answer("Ты зачем сюда жмакаешь?")


@update_project.callback_query(AdminCallbackProjectUpdateMenu.filter())
async def process_update_menu(
    query: CallbackQuery, callback_data: ProjectList, state: FSMContext
):
    match callback_data.action:
        case "add_pic":
            await state.set_state(UpdateProject.add_pic)
            await query.message.delete()
            await query.message.answer(
                "Жду пикчу, чтобы убрать пикчу напиши /empety",
                reply_markup=CancelButton.build("update"),
            )
        case "add_git":
            await state.set_state(UpdateProject.add_git)
            await query.message.delete()
            await query.message.answer(
                "Жду ссылку, чтобы убрать ссылку напиши /empety",
                reply_markup=CancelButton.build("update"),
            )
        case "update_project":
            await state.set_state(UpdateProject.update_base)
            data = await state.get_data()
            msg = await add_project_final_msg(data)
            await query.message.edit_text(
                msg + "\n\n <b>Выберите что нужно изменить:</b>",
                reply_markup=update_base_info_kb(),
            )

@update_project.message(
    StateFilter(UpdateProject.add_pic), F.photo
)
@update_project.message(StateFilter(UpdateProject.add_pic),F.text == "/empety")
@connection()
async def process_add_pic(message: Message, state: FSMContext, session, **kwargs):
    try:
        data = await state.get_data()
        project_info = await ProjectDAO.find_one_or_none(
            session=session, filters=ProjectNameModel(name=data.get("name"))
        )
        if message.text == '/empety':
            project_info.img_id = None
        else:
            project_info.img_id = message.photo[-1].file_id
        project_info = ProjectModel.model_validate(project_info)
        await ProjectDAO.update(
                session=session,
                filters=ProjectNameModel(name=data.get("name")),
                values=project_info,
            )
        await message.answer('Превью было изменено',reply_markup=MainKeyboard.build_project_cotrol_panel())
        await state.set_state(AdminPanelStates.project_control)
    except Exception as e:
        logger.error(
            f"Ошибка при добавлении пикчи к проекту: {e}"
        )
        await message.answer(
            "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова позже."
        )

@update_project.message(
    StateFilter(UpdateProject.add_git), F.text.regexp(https_link_pattern)
)
@update_project.message(StateFilter(UpdateProject.add_git),F.text == "/empety")
@connection()
async def process_add_git(message: Message, state: FSMContext, session, **kwargs):
    try:
        data = await state.get_data()
        project_info = await ProjectDAO.find_one_or_none(
            session=session, filters=ProjectNameModel(name=data.get("name"))
        )
        if message.text == '/empety':
            project_info.github_link = None
        else:
            project_info.github_link = message.text
        project_info = ProjectModel.model_validate(project_info)
        await ProjectDAO.update(
                session=session,
                filters=ProjectNameModel(name=data.get("name")),
                values=project_info,
            )
        await message.answer('Ссылка изменена',reply_markup=MainKeyboard.build_project_cotrol_panel())
        await state.set_state(AdminPanelStates.project_control)
    except Exception as e:
        logger.error(
            f"Ошибка при добавлении ссылки к проекту: {e}"
        )
        await message.answer(
            "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова позже."
        )


@update_project.message( StateFilter(UpdateProject.add_git), ~F.text.regexp(https_link_pattern))
async def not_reqexp_add_git(message: Message, state: FSMContext):
    await message.answer('Это не похоже на ссылку',reply_markup=CancelButton.build("update"))


@update_project.callback_query(StateFilter(UpdateProject.update_base),AdminCallbackProjectUpdateBaseInfo.filter())
@connection()
async def process_update_project_qr(
    query: CallbackQuery,
    callback_data: AdminCallbackProjectUpdateBaseInfo,
    state: FSMContext,
    session,
    **kwargs,
):
    data = await state.get_data()
    match callback_data.action:
        case "save":
            project_info = (
                await ProjectDAO.find_one_or_none(
                    session=session, filters=ProjectNameModel(name=data.get("name"))
                )
            ).to_dict()
            project_info.update(data)
            project_info = ProjectModel.model_validate(project_info)
            await ProjectDAO.update(
                session=session,
                filters=ProjectNameModel(name=data.get("name")),
                values=project_info,
            )
            await query.message.delete()
            await query.message.answer("Данные обновленны", reply_markup=MainKeyboard.build_project_cotrol_panel())
            await state.set_state(AdminPanelStates.project_control)
        case _:
            await query.message.delete()
            await state.update_data({"update_data": callback_data.action})
            await state.set_state(UpdateProject.take_data_to_update)
            await query.message.answer(
                "Введите новые данные", reply_markup=CancelButton.build("update")
            )


@update_project.message(StateFilter(UpdateProject.take_data_to_update), ~F.text)
async def warning_not_text(message: Message):
    await message.answer("Только текст,брача")


@update_project.message(StateFilter(UpdateProject.take_data_to_update))
async def process_update_project_msg(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data({data["update_data"]: message.text})
    await state.set_state(UpdateProject.update_base)
    data = await state.get_data()
    msg = await add_project_final_msg(data)
    await message.answer(
        msg + "\n\n <b>Выберите что нужно изменить:</b>",
        reply_markup=update_base_info_kb(),
    )

import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from loguru import logger
from app.bot.admin.common import (
    add_project_final_msg,
    https_link_pattern,
)
from app.bot.schemas import ProjectModel, ProjectNameModel
from app.bot.dao import ProjectDAO
from app.bot.keyboard.inline_kb import (
    confirm_kb,
    change_kb,
    AdminCallbackProject,
    AdminCallbackProjectChange,
)
from app.bot.keyboard.markup_kb import CancelButton, MainKeyboard
from app.bot.admin.states import AddProject, AdminPanelStates
from app.dao.database import connection
create_project = Router()



@create_project.message(~F.text, StateFilter(AddProject))
async def warning_not_text(message: Message):
    await message.answer("Я ожидаю от тебя текст, а не что-то другое")


@create_project.message(F.text == MainKeyboard.get_project_contol_kb().get("add_project"), StateFilter(AdminPanelStates.project_control))
async def add_new_project(message: Message, state: FSMContext):
    await state.set_state(AddProject.name)
    await message.answer(
        "Введите название проекта:", reply_markup=CancelButton.build("create")
    )


@create_project.message(
    StateFilter(AddProject) and F.text == CancelButton.get_cancel_texts().get("create")
)
async def cancel_dialog(message: Message, state: FSMContext):
    await state.set_state(AdminPanelStates.project_control)
    await message.answer(
        f"Окей, отменяю", reply_markup=MainKeyboard.build_project_cotrol_panel()
    )


@create_project.message(StateFilter(AddProject.name))
@connection()
async def process_name(message: Message, state: FSMContext, session, **kwargs):
    project = await ProjectDAO.find_one_or_none(
        session=session, filters=ProjectNameModel(name=message.text)
    )
    if project:
        await message.answer(
            "Проект с таким названием уже существует, попробуйте снова"
        )
        return
    await state.update_data({"name": message.text})
    await state.set_state(AddProject.description_small)
    await message.answer(
        f"Введите краткое описание проекта", reply_markup=CancelButton.build("create")
    )


@create_project.message(StateFilter(AddProject.description_small))
async def process_description_small(message: Message, state: FSMContext):
    await state.update_data({"description_small": message.text})
    await state.set_state(AddProject.description_large)
    await message.answer(
        f"Введите полное описание проекта", reply_markup=CancelButton.build("create")
    )


@create_project.message(StateFilter(AddProject.description_large))
async def process_description_large(message: Message, state: FSMContext):
    await state.update_data({"description_large": message.text})
    await state.set_state(AddProject.telegram_bot_url)
    await message.answer(f"Введите тег бота", reply_markup=CancelButton.build("create"))


@create_project.message(
    F.text,
    StateFilter(AddProject.telegram_bot_url),
)
async def process_telegram_bot_url(message: Message, state: FSMContext):
    await state.update_data({"telegram_bot_url": message.text})
    data = await state.get_data()
    logger.info(data)
    msg = await add_project_final_msg(data)
    await message.answer(msg + "\n\nПодтвердите публикацию", reply_markup=confirm_kb())
    await state.set_state(AddProject.confirm)



@create_project.callback_query(AdminCallbackProject.filter())
@connection()
async def process_confirm(
    query: CallbackQuery,
    callback_data: AdminCallbackProject,
    state: FSMContext,
    session,
    **kwargs,
):
    if callback_data.action == "yes":
        data = await state.get_data()
        values = ProjectModel(
            name=data.get("name"),
            description_small=data.get("description_small"),
            description_large=data.get("description_large"),
            telegram_bot_url=data.get("telegram_bot_url"),
        )
        await ProjectDAO.add(session, values)
        await query.message.delete()
        await query.message.answer(
            "Добавление прошло успешно",
            reply_markup=MainKeyboard.build_project_cotrol_panel(),
        )
        await state.set_state(AdminPanelStates.project_control)
    elif callback_data.action == "no":
        await query.message.delete()
        await query.message.answer(
            "Понял, отменяю публикацию",
            reply_markup=MainKeyboard.build_project_cotrol_panel(),
        )
        await state.set_state(AdminPanelStates.project_control)
    elif callback_data.action == "change":
        await query.message.edit_text(
            query.message.text.replace(
                "\n\nПодтвердите публикацию", "\n\nВыберите что нужно поменять:"
            ),
            reply_markup=change_kb(),
        )
        await state.set_state(AddProject.change)


@create_project.callback_query(
    StateFilter(AddProject.change) and AdminCallbackProjectChange.filter()
)
async def process_change_qr(
    query: CallbackQuery, callback_data: AdminCallbackProjectChange, state: FSMContext
):
    if callback_data.action == "back":
        await query.message.delete()
        data = await state.get_data()
        msg = await add_project_final_msg(data)
        await query.message.answer(
            msg + "\n\nПодтвердите публикацию", reply_markup=confirm_kb()
        )
        return
    await query.message.delete()
    await query.message.answer(
        "Теперь введите заменяющее значение", reply_markup=CancelButton.build("create")
    )
    await state.update_data({"changed_state": callback_data.action})


@create_project.message(StateFilter(AddProject.change))
async def process_change_msg(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data({data.get("changed_state"): message.text})
    await state.set_state(AddProject.confirm)
    data = await state.get_data()
    msg = await add_project_final_msg(data)
    await message.answer(msg + "\n\nПодтвердите публикацию", reply_markup=confirm_kb())

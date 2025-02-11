from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger
from aiogram.filters.callback_data import CallbackData


class AdminCallback(CallbackData, prefix="admin_confirm_project"):
    action: str
    project_name:str

def confirm_kb(project_name:str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    logger.debug(AdminCallback.filter())
    kb.button(
        text="✅ Подтвердить",
        callback_data=AdminCallback(
            action="yes",
            project_name = project_name
        ).pack()
    )
    kb.button(
        text="❌ Отклонить",
        callback_data=AdminCallback(
            action="no",
            project_name = project_name
        ).pack()
    )
    kb.adjust(2)
    return kb.as_markup()
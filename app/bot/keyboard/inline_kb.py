from typing import Optional
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger
from aiogram.filters.callback_data import CallbackData
from bot.admin.common import state_dict

class AdminCallbackAddProject(CallbackData, prefix="add_project"):
    action: str

class AdminCallbackAddProjectChange(CallbackData, prefix="add_project_change"):
    action:str

def confirm_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(
        text="✅ Подтвердить",
        callback_data=AdminCallbackAddProject(
            action="yes",
        ).pack()
    )
    kb.button(
        text="❌ Отклонить",
        callback_data=AdminCallbackAddProject(
            action="no",
        ).pack()
    )
    kb.button(
        text="❌ Изменить",
        callback_data=AdminCallbackAddProject(
            action="change",
        ).pack()
    )
    kb.adjust(2)
    return kb.as_markup()


def change_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for key,val in state_dict.items():
        kb.button(
            text=val,
            callback_data=AdminCallbackAddProjectChange(
                action = key
            ).pack()
        )
    kb.adjust(3)
    return kb.as_markup()
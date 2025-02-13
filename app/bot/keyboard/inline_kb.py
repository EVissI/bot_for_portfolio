from typing import Optional
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger
from aiogram.filters.callback_data import CallbackData
from bot.admin.common import state_dict

class AdminCallbackProject(CallbackData, prefix="add_project"):
    action: str

class AdminCallbackDeleteProject(CallbackData, prefix="delete_project"):
    action: str

class AdminCallbackProjectChange(CallbackData, prefix="project_change"):
    action:str

class AdminCallbackProjectUpdate(CallbackData, prefix="project_update"):
    action:str

class VoteProject(CallbackData, prefix="rating"):
    vote:int
    project_name:str
    telegram_id:int

def confirm_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(
        text="✅ Подтвердить",
        callback_data=AdminCallbackProject(
            action="yes",
        ).pack()
    )
    kb.button(
        text="❌ Отклонить",
        callback_data=AdminCallbackProject(
            action="no",
        ).pack()
    )
    kb.button(
        text="⚙ Изменить",
        callback_data=AdminCallbackProject(
            action="change",
        ).pack()
    )
    kb.adjust(2)
    return kb.as_markup()

def confirm_del_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="✅ Удалить",
        callback_data=AdminCallbackDeleteProject(
            action="yes",
        ).pack()
    )
    kb.button(
        text="❌ Оставить",
        callback_data=AdminCallbackDeleteProject(
            action="no",
        ).pack()
    )
    kb.adjust(2)
    return kb.as_markup()


def change_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for key,val in state_dict.items():
        kb.button(
            text=val,
            callback_data=AdminCallbackProjectChange(
                action = key
            ).pack()
        )
    kb.button(text='<--Назад',
            callback_data=AdminCallbackProjectChange(
                action = 'back'
            ).pack())
    kb.adjust(1)
    return kb.as_markup()   

def update_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for key,val in state_dict.items():
        kb.button(
            text=val,
            callback_data=AdminCallbackProjectUpdate(
                action = key
            ).pack()
        )
    kb.button(text='👌Сохранить',
            callback_data=AdminCallbackProjectUpdate(
                action = 'save'
            ).pack())
    kb.adjust(1)
    return kb.as_markup()   

def vote_rating_kb(project_name:str,telegram_id:int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="💩",
        callback_data=VoteProject(
            vote=1,
            project_name=project_name,
            telegram_id=telegram_id
        ).pack()
    )
    kb.button(
        text="😐",
        callback_data=VoteProject(
            vote=2,
            project_name=project_name,
            telegram_id=telegram_id
        ).pack()
    )
    kb.button(
        text="🙂",
        callback_data=VoteProject(
            vote=3,
            project_name=project_name,
            telegram_id=telegram_id
        ).pack()
    )
    kb.button(
        text="😀",
        callback_data=VoteProject(
            vote=4,
            project_name=project_name,
            telegram_id=telegram_id
        ).pack()
    )
    kb.button(
        text="🤩",
        callback_data=VoteProject(
            vote=5,
            project_name=project_name,
            telegram_id=telegram_id
        ).pack()
    )
    kb.adjust(5)
    return kb.as_markup() 
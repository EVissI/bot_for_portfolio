from typing import Optional
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger
from aiogram.filters.callback_data import CallbackData
from bot.admin.common import state_dict

class AdminCallbackProject(CallbackData, prefix="add_project"):
    action: str

class ProjectList(CallbackData, prefix="add_project"):
    name: Optional[str]
    page: int = 0

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

def project_list_kb(project_names:list[str],page=0)-> InlineKeyboardMarkup:
    max_buttons = 6 
    kb = InlineKeyboardBuilder()

    start_idx = page * max_buttons
    end_idx = start_idx + max_buttons
    current_objects = project_names[start_idx:end_idx]

    for obj in current_objects:
        kb.button(text=obj, callback_data=ProjectList(
            name= obj,
            page=page
        ).pack())

    if len(project_names) > max_buttons:
        if page > 0:
            kb.button(text="<-", callback_data=ProjectList(
                name= None,
                page=page -1 
            ).pack())

        if end_idx < len(project_names): 
            kb.button(text="->", callback_data=ProjectList(
                name= None,
                page=page +1 
            ).pack())

    kb.adjust(3,3,2)
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
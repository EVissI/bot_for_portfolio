from typing import Dict
from aiogram.types import ReplyKeyboardMarkup,ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from loguru import logger
from bot.models import User

del_kbd = ReplyKeyboardRemove()



class MainKeyboard:
    user_kb_texts_dict = {
        'my_projects': 'Мои проекты',
        'contacts': 'Способы связи'
    }

    admin_kb_texts_dict = {
        'add_project': 'Добавить проект',
        'change_project': 'Изменить проект',
        'delete_project': 'Удалить проект'
    }

    @staticmethod
    def get_user_kb_texts() -> Dict[str, str]:
        """
        'my_projects'\n
        'contacts
        """
        return MainKeyboard.user_kb_texts_dict

    @staticmethod
    def get_admin_kb_texts() -> Dict[str, str]:
        """
        'add_project'\n
        'change_project'\n
        'delete_project'
        """
        return MainKeyboard.admin_kb_texts_dict

    @staticmethod
    def build(user_role: User.Role) -> ReplyKeyboardMarkup:
        kb = ReplyKeyboardBuilder()

        for val in MainKeyboard.user_kb_texts_dict.values():
            kb.button(text=val)
        kb.adjust(len(MainKeyboard.user_kb_texts_dict))

        if user_role == User.Role.Admin:
            for val in MainKeyboard.admin_kb_texts_dict.values():
                kb.button(text=val)
            kb.adjust(len(MainKeyboard.user_kb_texts_dict), len(MainKeyboard.admin_kb_texts_dict))

        return kb.as_markup(resize_keyboard=True)


def cancel_button(text_key:str) -> ReplyKeyboardMarkup:
    """
    text_keys:\n
        'create'\n
        'delete'\n
        'update'
    """
    cancel_texts_dict = {
        'create':'Отменить создание',
        'delete':'Отменить удаление',
        'update':'Отменить изменение'
    }
    kb = ReplyKeyboardBuilder()
    kb.button(text = cancel_texts_dict.get(text_key))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


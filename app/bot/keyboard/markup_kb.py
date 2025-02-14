from typing import Dict
from aiogram.types import ReplyKeyboardMarkup,ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from loguru import logger
from bot.models import User

del_kbd = ReplyKeyboardRemove()



class MainKeyboard:
    user_kb_texts_dict = {
        'my_projects': 'Мои проекты',
        'contacts': 'Мой тг'
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


class CancelButton:
    cancel_texts_dict = {
        'create': 'Отменить создание',
        'delete': 'Отменить удаление',
        'update': 'Отменить изменение'
    }

    @staticmethod
    def build(text_key: str) -> ReplyKeyboardMarkup:
        """
        'create'\n
        'delete'\n
        'update'
        """
        kb = ReplyKeyboardBuilder()
        cancel_text = CancelButton.cancel_texts_dict.get(text_key)
        
        if cancel_text:
            kb.button(text=cancel_text)
        
        kb.adjust(1) 
        return kb.as_markup(resize_keyboard=True)
    
    @staticmethod
    def get_cancel_texts()->Dict[str, str]:
        """
        'create'\n
        'delete'\n
        'update'
        """
        return CancelButton.cancel_texts_dict

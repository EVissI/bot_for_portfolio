from typing import Dict
from aiogram.types import ReplyKeyboardMarkup,ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from loguru import logger

from app.bot.models import User

del_kbd = ReplyKeyboardRemove()

def back_button():
    kb = ReplyKeyboardBuilder()
    kb.button(text='Назад')
    return kb.as_markup(resize_keyboard=True)

class MainKeyboard:
    __user_kb_texts_dict = {
        'my_projects': 'Мои проекты',
        'contacts': 'Мой тг'
    }
    __admin_project_contol_kb_dict = {
        'add_project': 'Добавить проект',
        'change_project': 'Изменить проект',
        'delete_project': 'Удалить проект'
    }
    __admin_panel_kb_dict ={
        'project_panel': 'Управление проектами',
        'control_admins_panel': 'Управление администратоми'
    }

    __control_admins_kb_dict = {
        'give_administrator_rights': 'Дать права админа',
        'take_away_administrator_rights': 'Забрать права админа',
        'admin_list':'Списки администраторов'
    }

    @staticmethod
    def get_user_kb_texts() -> Dict[str, str]:
        """
        'my_projects'\n
        'contacts
        """
        return MainKeyboard.__user_kb_texts_dict

    @staticmethod
    def get_project_contol_kb() -> Dict[str, str]:
        """
        'add_project'\n
        'change_project'\n
        'delete_project'
        """
        return MainKeyboard.__admin_project_contol_kb_dict

    @staticmethod
    def get_control_admins_kb()-> Dict[str, str]:
        """
        'give_administrator_rights'\n
        'take_away_administrator_rights'\n
        'admin_list'
        """
        return MainKeyboard.__control_admins_kb_dict
    
    @staticmethod
    def get_admin_panel_kb_dict() -> Dict[str,str]:
        """
        'project_panel',\n
        'control_admins_panel'
        """
        return MainKeyboard.__admin_panel_kb_dict
    
    @staticmethod
    def build_main_kb(user_role: User.Role) -> ReplyKeyboardMarkup:
        kb = ReplyKeyboardBuilder()

        for val in MainKeyboard.get_user_kb_texts().values():
            kb.button(text=val)
        kb.adjust(len(MainKeyboard.get_user_kb_texts()))

        if user_role == User.Role.Admin:
            kb.button(text="Админ панель")
            kb.adjust(len(MainKeyboard.get_user_kb_texts()), 1)

        return kb.as_markup(resize_keyboard=True)
    
    @staticmethod
    def build_admin_panel() -> ReplyKeyboardMarkup:
        kb = ReplyKeyboardBuilder()
        for val in MainKeyboard.get_admin_panel_kb_dict().values():
            kb.button(text=val)
        kb.button(text='Назад')
        kb.adjust(len(MainKeyboard.get_admin_panel_kb_dict()),1)
        return kb.as_markup(resize_keyboard=True)
    
    @staticmethod
    def build_project_cotrol_panel() -> ReplyKeyboardMarkup:
        kb = ReplyKeyboardBuilder()

        for val in MainKeyboard.get_project_contol_kb().values():
            kb.button(text=val)

        kb.button(text='Назад')
        kb.adjust(len(MainKeyboard.get_user_kb_texts()), 1)
        return kb.as_markup(resize_keyboard=True)
    
    @staticmethod
    def build_admins_control_panel():
        kb = ReplyKeyboardBuilder()

        for val in MainKeyboard.get_control_admins_kb().values():
            kb.button(text=val)

        kb.button(text='Назад')
        kb.adjust(len(MainKeyboard.get_control_admins_kb()), 1)
        return kb.as_markup(resize_keyboard=True)

class CancelButton:
    cancel_texts_dict = {
        'create': 'Отменить создание',
        'delete': 'Отменить удаление',
        'update': 'Отменить изменение'
    }
    @staticmethod
    def get_cancel_texts()->Dict[str, str]:
        """
        'create'\n
        'delete'\n
        'update'
        """
        return CancelButton.cancel_texts_dict

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
    


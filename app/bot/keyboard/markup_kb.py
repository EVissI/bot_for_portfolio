from aiogram.types import ReplyKeyboardMarkup,ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from bot.models import User

del_kbd = ReplyKeyboardRemove()
user_kb_texts_dict={'my_projects':'Мои проекты',
                'contacts': 'Способы связи'}

admin_kb_texts_dict={'add_project':'Добавить проект',
                'change_project':'Изменить проект',
                'delete_porject':'Удалить проект'}

def main_keyboard(user_role: User.Role) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for val in user_kb_texts_dict.values():
        kb.button(text=val)
    kb.adjust(len(user_kb_texts_dict.values()))
    
    if user_role.value is User.Role.Admin.value:
        for val in admin_kb_texts_dict.values():
            kb.button(text = val)
        kb.adjust(len(user_kb_texts_dict.values()),len(admin_kb_texts_dict.values()))
    return kb.as_markup(resize_keyboard=True)


def cancel_button() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text = "Отменить создание")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


from aiogram.types import ReplyKeyboardMarkup,ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from bot.models import User

del_kbd = ReplyKeyboardRemove()


def main_keyboard(user_role: User.Role) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Мои проекты")
    kb.button(text="Способы связи")
    kb.adjust(2)
    if user_role is User.Role.Admin:
        kb.button(text ='Добавить проект')
        kb.button(text = 'Изменить проект')
        kb.button(text = 'Удалить проект')
    return kb.as_markup(resize_keyboard=True)

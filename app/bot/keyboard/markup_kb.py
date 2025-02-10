from aiogram.types import ReplyKeyboardMarkup,ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from bot.models import User

del_kbd = ReplyKeyboardRemove()


def main_keyboard(user_role: User.Role) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Тест")
    kb.adjust(1)
    if user_role is User.Role.Admin:
        kb.button(text ='Тест')
        kb.button(text = 'Тест')
    return kb.as_markup(resize_keyboard=True)

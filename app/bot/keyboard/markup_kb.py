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
        kb.adjust(2,3)
    return kb.as_markup(resize_keyboard=True)


def skip_button() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text = "Пропустить")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


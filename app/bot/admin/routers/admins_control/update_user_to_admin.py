from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from loguru import logger
from app.bot.models import User
from app.bot.schemas import TelegramIDModel, UserModel
from app.bot.dao import UserDAO
from app.bot.keyboard.markup_kb import MainKeyboard, back_button
from app.bot.admin.states import AdminPanelStates, GiveAdminRight
from app.dao.database import connection
from app.config import bot
give_administrator_rights_router = Router()


@give_administrator_rights_router.message(
    F.text == MainKeyboard.get_control_admins_kb().get("give_administrator_rights"),
    StateFilter(AdminPanelStates.admins_control),
)
async def cmd_give_administrator_rights(message: Message, state: FSMContext):
    await message.answer(
        "Введите telegram_id юзера для повышения прав", reply_markup=back_button()
    )
    await state.set_state(GiveAdminRight.id)


@give_administrator_rights_router.message(
    F.text == "Назад", StateFilter(GiveAdminRight.id)
)
async def back(message: Message, state: FSMContext):
    await message.reply(
        message.text, reply_markup=MainKeyboard.build_admins_control_panel()
    )
    await state.set_state(AdminPanelStates.admins_control)


@give_administrator_rights_router.message(
    F.text.regexp(r"^\d+$"), StateFilter(GiveAdminRight.id)
)
@connection()
async def update_user_rights(message: Message, state: FSMContext, session, **kwargs):
    try:
        user = await UserDAO.find_one_or_none(
            session=session, filters=TelegramIDModel(telegram_id=message.text)
        )
        if not user:
            await message.answer(
                "Не нашел такого юзера, попробуй еще раз", reply_markup=back_button()
            )
            return
        user.role = User.Role.Admin
        user = UserModel.model_validate(user)
        await UserDAO.update(
            session=session,
            filters=TelegramIDModel(telegram_id=message.text),
            values=user,
        )
        await message.answer(
            f"{user.first_name}({user.telegram_id}) был успешно повышен до админа",reply_markup=MainKeyboard.build_admins_control_panel()
        )
        await state.set_state(AdminPanelStates.admins_control)
        await bot.send_message(user.telegram_id,'🥳 ты теперь админ ура ура ура',reply_markup=MainKeyboard.build_main_kb(User.Role.Admin))
    except Exception as e:
        logger.error(f"Ошибка при повышении юзера до админа: {e}")
        await message.answer(
            "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова позже."
        )


@give_administrator_rights_router.message(
    ~F.text.regexp(r"^\d+$"), StateFilter(GiveAdminRight.id)
)
async def update_user_rights(message: Message, state: FSMContext):
    await message.answer(
        "Это не похоже на телеграм id, попробуйка еще раз", reply_markup=back_button()
    )


@give_administrator_rights_router.message(
    ~F.text, StateFilter(AdminPanelStates.admins_control)
)
async def is_not_text(message: Message):
    await message.answer("Только текст, брача")

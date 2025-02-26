from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from loguru import logger
from bot.keyboard.inline_kb import AdminLowerAdminToUser, admin_inline_list_kb
from bot.models import User
from bot.schemas import TelegramIDModel, UserModel
from bot.dao import UserDAO
from bot.keyboard.markup_kb import MainKeyboard
from dao.database import connection
from bot.admin.states import AdminPanelStates
from config import settings
remove_administrator_rights_router = Router()


@remove_administrator_rights_router.message(
    F.text == MainKeyboard.get_control_admins_kb().get("take_away_administrator_rights"),
    StateFilter(AdminPanelStates.admins_control)
)
@connection()
async def cmd_give_administrator_rights(
    message: Message, state: FSMContext, session, **kwargs
):
    admin_list = await UserDAO.get_admins(session)
    await message.answer(
        "Выбери админа которого хочешь понизить в звании",
        reply_markup=admin_inline_list_kb(admin_list),
    )


@remove_administrator_rights_router.callback_query(AdminLowerAdminToUser.filter())
@connection()
async def process_removing_admin_rights(
    query: CallbackQuery,
    callback_data: AdminLowerAdminToUser,
    state: FSMContext,
    session,
    **kwargs,
):
    try:
        match callback_data.action:
            case "update":
                if query.from_user.id == callback_data.telegram_id:
                    await query.answer('Ты же не думал, что я дам понизить самого себя:)')
                    return
                if callback_data.telegram_id in settings.ROOT_ADMIN_IDS:
                    await query.answer('Ага, размечтался:)')
                    return
                admin = await UserDAO.find_one_or_none(
                    session=session,
                    filters=TelegramIDModel(telegram_id=callback_data.telegram_id),
                )
                admin.role = User.Role.User
                admin = UserModel.model_validate(admin)
                await UserDAO.update(
                    session=session,
                    filters=TelegramIDModel(telegram_id=callback_data.telegram_id),
                    values=admin,
                )
                await query.message.delete()
                await query.message.answer(
                    f"Теперь {admin.first_name}[{admin.telegram_id}] понижен в звании и является обычным обывалой",
                    reply_markup=MainKeyboard.build_admins_control_panel(),
                )
                await state.set_state(AdminPanelStates.admins_control)
            case "cancel":
                await query.message.delete()
                await query.message.answer(
                    "Пон, возвращаю в меню",
                    reply_markup=MainKeyboard.build_admins_control_panel(),
                )
                await state.set_state(AdminPanelStates.admins_control)
    except Exception as e:
        logger.error(
            f"Ошибка при понижении админа до юзера: {e}"
        )
        await query.answer(
            "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова позже."
        )
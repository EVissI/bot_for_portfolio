from aiogram import Router,F
from aiogram.types import Message
from aiogram.filters import StateFilter

from aiogram.fsm.context import FSMContext

from bot.models import User
from bot.admin.routers.projects_control.create_router import create_project
from bot.admin.routers.projects_control.delete_router import delete_project
from bot.admin.routers.projects_control.update_router import update_project

from bot.admin.routers.admins_control.admins_list import admin_list_router
from bot.admin.routers.admins_control.update_admin_to_user import remove_administrator_rights_router
from bot.admin.routers.admins_control.update_user_to_admin import give_administrator_rights_router
from bot.keyboard.markup_kb import MainKeyboard
from bot.admin.states import AdminPanelStates

admin_router = Router()
admin_router.include_router(create_project)
admin_router.include_router(delete_project)
admin_router.include_router(update_project)

admin_router.include_router(admin_list_router)
admin_router.include_router(remove_administrator_rights_router)
admin_router.include_router(give_administrator_rights_router)

@admin_router.message(F.text == 'Админ панель')
async def change_to_admin_kb(message:Message,state:FSMContext):
    await message.reply(message.text,reply_markup=MainKeyboard.build_admin_panel())
    await state.set_state(AdminPanelStates.admin_panel)

@admin_router.message(F.text == MainKeyboard.get_admin_panel_kb_dict().get('project_panel'),StateFilter(AdminPanelStates.admin_panel))
async def cmd_project_control_panel(message:Message,state:FSMContext):
    await message.reply(message.text,reply_markup=MainKeyboard.build_project_cotrol_panel())
    await state.set_state(AdminPanelStates.project_control)

@admin_router.message(F.text == MainKeyboard.get_admin_panel_kb_dict().get('control_admins_panel'),StateFilter(AdminPanelStates.admin_panel))
async def cmd_admins_control_panel(message:Message,state:FSMContext):
    await message.reply(message.text,reply_markup=MainKeyboard.build_admins_control_panel())
    await state.set_state(AdminPanelStates.admins_control)

@admin_router.message(F.text == 'Назад',StateFilter(AdminPanelStates.admin_panel))
async def cmd_admins_control_panel(message:Message,state:FSMContext):
    await message.reply(message.text,reply_markup=MainKeyboard.build_main_kb(User.Role.Admin))
    await state.clear()

@admin_router.message(F.text == 'Назад',StateFilter(AdminPanelStates.project_control,AdminPanelStates.admins_control))
async def cmd_admins_control_panel(message:Message,state:FSMContext):
    await message.reply(message.text,reply_markup=MainKeyboard.build_admin_panel())
    await state.set_state(AdminPanelStates.admin_panel)
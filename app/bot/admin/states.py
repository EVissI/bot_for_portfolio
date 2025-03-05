from aiogram.fsm.state import StatesGroup, State

class AdminPanelStates(StatesGroup):
    admin_panel = State()
    project_control = State()
    admins_control = State()

class UpdateProject(StatesGroup):
    name = State()
    update_menu = State()
    update_base = State()
    add_pic = State()
    add_git = State()
    take_data_to_update = State()

class DeleteProject(StatesGroup):
    name = State()
    confirm = State()

class GiveAdminRight(StatesGroup):
    id = State()

class AddProject(StatesGroup):
    name = State()
    description_small = State()
    description_large = State()
    telegram_bot_url = State()
    confirm = State()
    change = State()
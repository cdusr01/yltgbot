from aiogram.dispatcher.filters.state import StatesGroup, State

class RoleStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_role_number = State()
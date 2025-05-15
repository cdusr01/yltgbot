from aiogram.dispatcher.filters.state import StatesGroup, State

class OrderStates(StatesGroup):
    waiting_for_order_type = State()
    waiting_for_order_details = State()
    waiting_for_files = State()
    waiting_for_response = State()
    waiting_for_pay = State()
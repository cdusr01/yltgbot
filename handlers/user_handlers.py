from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart

from service.freelancer_service import FreelancerService
from service.role_service import RoleService
from service.status_service import StatusService
from service.user_service import UserService
from service.order_service import OrderService
from utils.keyboards import get_subjects_keyboard, get_payment_keyboard
from utils.logger import log_interaction, log_exception

from service.models import User


user_service = UserService()
order_service = OrderService()
status_service = StatusService()
freelancer_service = FreelancerService()
role_service = RoleService()

async def command_start_handler(message: types.Message, state: FSMContext):
    """Обработчик команды /start"""
    await message.answer(f"Привет, {message.from_user.full_name}!")

    user = user_service.get_by_user_id(message.from_user.id)
    if not user:
        user_service.save(User(
            id=None,
            user_id=message.from_user.id,
            user_tag=message.from_user.username or str(message.from_user.id),
            role_id=5,
            balance=0
        ))
    else:
        await log_interaction(f"User {user.user_id} updated username")

        await send_menu(message)
        await log_interaction(f"{message.from_user.id} used /start")

async def send_menu(message: types.Message):
    """Отправка меню с предметами"""
    user = user_service.get_by_user_id(message.from_user.id)
    orders = order_service.get_all_user_orders(user.id)
    if orders == None or len(list(filter(lambda x: x.status_id < 3, orders))) < 5:
        keyboard = get_subjects_keyboard()
        await message.answer("📚Список возможных предметов:", reply_markup=keyboard)
    else:
        await message.answer("У вас слишком много заказов, подождите!")

async def send_queue_position(from_user, user_id: int):
    bot = Dispatcher.get_current().bot
    global last_order_id
    try:
        all_orders = order_service.get_all()
        user_orders = [order for order in all_orders if order.user_id == user_id and order.status_id != 3]
        if user_orders:
            s = '\n'.join(list(map(lambda
                                       x: f"Заказ #{x.id} находится в очереди. Позиция - {all_orders.index(x) + 1}. Состояние: {status_service.get_by_id(x.status_id).state}",
                                   user_orders)))
            last_order_id = user_orders[-1].id
        else:
            s = "У вас нет активных заказов"
        await bot.send_message(from_user, s)
        return last_order_id
    except Exception as e:
        await log_exception(e, "send_queue_position")

async def menu_handler(message: types.Message, state: FSMContext):
    """Обработчик команды /menu"""
    await send_menu(message)
    await log_interaction(f"{message.from_user.id} used /menu")

async def get_queue_position_handler(message: types.Message):
    """Обработчик команды /position"""
    user = user_service.get_by_user_id(message.from_user.id)
    await send_queue_position(message.from_user.id, user.id)
    await log_interaction(f"{message.from_user.id} checked position")

async def get_profile(message: types.Message):
    """Обработчик команды /profile"""
    user = user_service.get_by_user_id(message.from_user.id)
    role = role_service.get_by_id(user.role_id)
    if user.role_id < 5:
        freelancer = freelancer_service.get_by_user_id(user.id)
        await message.answer(f"Профиль:\nИмя: {message.from_user.full_name}\nUser-id: {message.from_user.id}\nВыполнено заказов: {freelancer.amount}\nБаланс: {freelancer.salary}₽\nСтавка: {role.rate}%")

async def update_balance(query: types.CallbackQuery):
    await query.message.answer("Меню пополнения баланса:", reply_markup=get_payment_keyboard())

async def send_created_bill(query: types.CallbackQuery):
    pass

def register_user_handlers(dp):
    dp.register_message_handler(command_start_handler, CommandStart())
    dp.register_message_handler(menu_handler, commands=["menu"])
    dp.register_message_handler(get_queue_position_handler, commands=["position"])
    dp.register_message_handler(get_profile, commands=["profile"])
    dp.register_callback_query_handler(
        update_balance,
        lambda c: c.data == "update-balance"
    )
    dp.register_callback_query_handler(
        send_created_bill,
        lambda c: c.data == "create-bill"
    )
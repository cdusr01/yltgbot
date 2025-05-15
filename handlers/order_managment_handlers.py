from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup

from handlers.user_handlers import send_menu
from service.file_service import FileService
from service.freelancer_service import FreelancerService
from service.order_service import OrderService
from service.order_types_service import OrderTypeService
from service.status_service import StatusService
from service.subject_service import SubjectService
from service.user_service import UserService
from states.order_states import OrderStates
from utils.keyboards import get_order_actions_keyboard, get_orders_list_keyboard, get_cancel_order_button
from utils.logger import log_interaction, log_exception

order_service = OrderService()
user_service = UserService()
status_service = StatusService()
freelancer_service = FreelancerService()
file_service = FileService()
order_type_service = OrderTypeService()
subnject_service = SubjectService()


async def show_available_orders(message: types.Message):
    """Показать все доступные заказы (статус 'В ожидании')"""
    user = user_service.get_by_user_id(message.from_user.id)

    if user.role_id >= 5:  # Проверка прав (только для не-админов)
        return

    orders = order_service.get_orders_by_status_id(1)  # Статус 1 - "В ожидании"
    if not orders:
        await message.answer("Нет доступных заказов")
        return

    keyboard = get_orders_list_keyboard(orders)
    await message.answer("📋 Список доступных заказов:", reply_markup=keyboard)
    await log_interaction(f"User {message.from_user.id} viewed orders list")


async def view_order_details(callback: types.CallbackQuery):
    """Показать детали конкретного заказа"""
    order_id = int(callback.data.split("-")[1])
    order = order_service.get_by_id(order_id)
    user = user_service.get_by_user_id(callback.from_user.id)

    # Формируем текст заказа
    order_text = f"""
📝 Заказ #{order.id}
————————————
🗂 Тип: {order_type_service.get_by_id(order.order_type_id).name}
📚 Предмет: {subnject_service.get_by_id(order.subject_id).name}
🔮 Статус: {status_service.get_by_id(order.status_id).state}
————————————
📄 Описание:
{order.order_text}
    """

    # Получаем клавиатуру с действиями
    keyboard = get_order_actions_keyboard(order, user)

    await callback.message.edit_text(order_text, reply_markup=keyboard)
    await log_interaction(f"User {callback.from_user.id} viewed order {order.id}")


async def accept_order(callback: types.CallbackQuery, state: FSMContext):
    """Принять заказ в работу"""
    order_id = int(callback.data.split("-")[1])
    user = user_service.get_by_user_id(callback.from_user.id)

    order = order_service.get_by_id(order_id)
    order.freelancer_id = user.id
    order.status_id = 2  # Статус "В процессе"
    order_service.update(order)


    async with state.proxy() as data:
        data['order_id'] = order.id
        data['step'] = 'accept_order'

    # Отправляем файлы если есть
    order_files = file_service.get_file(order_id)
    print(order_files)
    if order_files:
        await callback.bot.send_document(
            callback.from_user.id,
            document=order_files,
            caption=f"Файлы к заказу #{order.id}"
        )

    await callback.message.edit_text(f"✅ Вы приняли заказ #{order.id}",
                                     reply_markup=InlineKeyboardMarkup().add(get_cancel_order_button()))
    await OrderStates.waiting_for_response.set()
    await log_interaction(f"User {callback.from_user.id} accepted order {order.id}")


async def submit_order_response(message: types.Message, state: FSMContext):
    """Отправить результат работы по заказу"""
    data = await state.get_data()
    order_id = data['order_id']
    freelancer = user_service.get_by_user_id(message.from_user.id)
    order = order_service.get_by_id(order_id)

    if not message.document:
        await message.answer("Пожалуйста, отправьте файл с результатом")
        return

    # Сохраняем файл ответа
    file_path = f"orders/{order_id}/response_{freelancer.id}_{message.document.file_name}"
    await message.document.download(destination_file=file_path)
    file_service.post_answer_file(order.user_id, order_id, file_path)

    # Уведомляем заказчика
    customer = user_service.get_by_id(order.user_id)
    await message.bot.send_document(
        customer.user_id,
        document=message.document.file_id,
        caption=f"✅ Ваш заказ #{order_id} выполнен!"
    )

    # Обновляем статус заказа
    order.status_id = 3
    order_service.update(order)

    # Статистика фрилансера
    order_type = order_type_service.get_by_id(order.order_type_id)
    freelancerst = freelancer_service.get_by_user_id(freelancer.id)
    freelancerst.amount = freelancerst.amount + 1
    freelancerst.salary = float(freelancerst.salary) + order_type.price
    freelancer_service.update(freelancerst)

    await message.answer("Результат успешно отправлен заказчику!")
    await state.finish()
    await log_interaction(f"Freelancer {freelancer.id} submitted response for order {order_id}")


async def cancel_order(query: types.CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        order_id = data["order_id"]
        order = order_service.get_by_id(order_id)
        order.status_id = 1
        order.freelancer_id = None
        order_service.update(order)
        await state.finish()
        await query.message.edit_text("Заказ отменён")
    except Exception as e:
        await log_exception(e, "cancel_order")

async def back_to_orders(query: types.CallbackQuery, state: FSMContext):
    try:
        orders = order_service.get_orders_by_status_id(1)
        if not orders:
            await query.message.edit_text("Нет доступных заказов")
            return

        keyboard = get_orders_list_keyboard(orders)
        await query.message.edit_text("📋 Список доступных заказов:", reply_markup=keyboard)
    except Exception as e:
        await log_exception(e, "back_to_orders")


def register_order_management_handlers(dp):
    dp.register_message_handler(
        show_available_orders,
        commands=["orders"],
        state="*"
    )

    dp.register_callback_query_handler(
        view_order_details,
        lambda c: c.data.startswith("view_order-"),
        state="*"
    )

    dp.register_callback_query_handler(
        accept_order,
        lambda c: c.data.startswith("accept_order-"),
        state="*"
    )

    dp.register_message_handler(
        submit_order_response,
        content_types=["document"],
        state=OrderStates.waiting_for_response
    )

    dp.register_callback_query_handler(
        cancel_order,
        lambda c: c.data == "cancel-order",
        state=OrderStates.waiting_for_response
    )
    dp.register_callback_query_handler(
        back_to_orders,
        lambda c: c.data == "back_to_orders"
    )

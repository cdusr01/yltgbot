import os
import uuid
from datetime import datetime
from zipfile import ZipFile

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType, InlineKeyboardMarkup, InlineKeyboardButton

from service.file_service import FileService
from service.models import Order
from service.order_service import OrderService
from service.order_types_service import OrderTypeService
from service.payment import Payment
from service.subject_service import SubjectService
from service.temp_order_service import TempOrderService
from service.user_service import UserService
from states.order_states import OrderStates
from utils.keyboards import (
    get_order_types_keyboard,
    get_cancel_keyboard, get_payment_keyboard, get_cancel_button
)
from utils.logger import log_interaction, log_exception

# Инициализация сервисов
order_service = OrderService()
user_service = UserService()
subject_service = SubjectService()
order_type_service = OrderTypeService()
file_service = FileService()
temp_order_service = TempOrderService()
payment = Payment()

# Глобальная переменная для временного хранения файлов
temp_files = {}


async def subject_callback_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.set_data({
        'user_id': callback.from_user.id,
        'created_at': str(datetime.now()),
        'step': 'subject_selection'
    })
    """Обработчик выбора предмета"""
    subject_id = int(callback.data.split("-")[1])
    await OrderStates.waiting_for_order_type.set()
    # await state.update_data(subject_id=subject_id)
    async with state.proxy() as data:
        data['subject_id'] = subject_id
        data['step'] = 'type_selection'
    keyboard = get_order_types_keyboard(subject_id)
    await callback.message.edit_text("📚Выберите услугу:", reply_markup=keyboard)
    await log_interaction(f"User {callback.from_user.id} selected subject {subject_id}")


async def order_type_callback_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик выбора типа заказа"""
    order_type_id = int(callback.data.split("-")[1])
    async with state.proxy() as data:
        data['order_type_id'] = order_type_id
        data['step'] = 'description_input'
    await OrderStates.waiting_for_order_details.set()

    await callback.message.edit_text(
        """📝Введите комментарий к заказу. Максимальная длина - 255 символов.
📎В случае необходимости далее будет возможность прикрепить файлы.
ℹ️Постарайтесь максимально подробно описать задачу.
ℹ️Если это лабораторная/практическая работа, то следует указать номер и вариант.
ℹ️В случае недостатка информации заказ может быть отменен!""",
        reply_markup=get_cancel_keyboard()
    )
    await log_interaction(f"User {callback.from_user.id} selected order type {order_type_id}")


async def process_order_details(message: types.Message, state: FSMContext):
    """Обработчик описания заказа"""
    if len(message.text) > 255:
        await message.answer("⚠️Описание должно быть не более 255 символов!")
        return

    async with state.proxy() as data:
        data['order_details'] = message.text
        data['step'] = 'file_upload'
    await OrderStates.waiting_for_files.set()

    await message.answer(
        "Приложите файлы (до 10):",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Готово", callback_data="finish_files")
        ).add(get_cancel_button())
    )
    await log_interaction(f"User {message.from_user.id} added order details")


async def handle_order_files(message: types.Message, state: FSMContext):
    """Обработчик файлов заказа"""
    async with state.proxy() as data:
        # Инициализируем список файлов если его нет
        if 'files' not in data:
            data['files'] = []
            data['temp_files'] = {}  # Локальное хранилище для текущего пользователя

        if len(data['temp_files']) >= 10:
            await message.answer("Максимум 10 файлов!")
            return

        file_info = None
        if message.content_type == ContentType.DOCUMENT:
            if message.document.file_size > 20 * 1024 * 1024:
                await message.answer("Файл слишком большой (макс. 20МБ)!")
                return
            file_info = {
                'file_id': message.document.file_id,
                'file_name': message.document.file_name,
                'type': 'document'
            }
            data['temp_files'][message.document.file_name] = message.document.file_id

        elif message.content_type == ContentType.PHOTO:
            file_info = {
                'file_id': message.photo[-1].file_id,
                'file_name': f'photo_{len(data["files"])}.jpg',
                'type': 'photo'
            }
            data['temp_files'][f"photo_{len(data['files'])}.jpg"] = message.photo[-1].file_id

        if file_info:
            data['files'].append(file_info)
            await message.answer(
                f"Файл сохранён ({len(data['temp_files'])}/10)",
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("Готово", callback_data="finish_files")
                ).add(get_cancel_button())
            )


async def finish_files_handler(callback: types.CallbackQuery, state: FSMContext):
    """Завершение приёма файлов"""
    try:
        data = await state.get_data()
        user = user_service.get_by_user_id(callback.from_user.id)

        order = Order(
            id=None,
            user_id=user.id,
            subject_id=data['subject_id'],
            order_type_id=data['order_type_id'],
            order_text=data['order_details'],
            is_urgent=True,
            status_id=1,
            freelancer_id=None
        )
        order_id = temp_order_service.save(order)

        async with state.proxy() as data:
            if 'files' in data and len(data['files']) != 0:
                if not os.path.exists(f"orders/{order_id}-{user.id}"):
                    os.mkdir(f"orders/{order_id}-{user.id}")
                zip_path = f"orders/{order_id}-{user.id}/order_files.zip"

                # Создаем уникальную папку для каждого пользователя/заказа

                # Скачиваем и упаковываем файлы
                with ZipFile(zip_path, 'w') as zipf:
                    for file_info in data['files']:
                        try:
                            file = await callback.bot.download_file_by_id(file_info['file_id'])
                            zipf.writestr(file_info['file_name'], file.read())
                        except Exception as e:
                            await log_exception(e, f"Error processing file {file_info['file_name']}: {e}")

                data['zip_path'] = str(zip_path)

        await OrderStates.waiting_for_pay.set()
        uid = uuid.uuid4()
        await state.update_data(order_id=order_id, user_id=user.id, uid=str(uid))
        url = payment.create_bill(order_type_service.get_by_id(order.order_type_id).price, uid)
        keyboard = get_payment_keyboard().add(InlineKeyboardButton(text="Ссылка на оплату", url=url)).add(
            get_cancel_button())
        await callback.message.answer(f"Заказ успешно сформирован, осталось лишь оплатить!", reply_markup=keyboard)

        await log_interaction(f"User {callback.from_user.id} created order {order_id}")
    except Exception as e:
        await log_exception(e, "finish_files_handler")


async def check_balance(query: types.CallbackQuery, state: FSMContext):
    bot = Dispatcher.get_current().bot
    data = await state.get_data()
    uid = data['uid']
    user_id = data['user_id']
    order_id = data['order_id']
    if payment.is_paid(uid):
        order = temp_order_service.get_by_id(order_id)
        new_order = order_service.save(order)
        if os.path.exists(f"orders/{order.id}-{user_id}/order_files.zip"):
            file_service.post_order_file(user_id, new_order, f'orders/{order.id}-{user_id}/order_files.zip')
        await state.finish()
        await query.message.answer(f"Заказ #{new_order} создан!\nДля отслеживания можно использовать /position")
        for i in user_service.get_all():
            if i.role_id < 5:
                try:
                    await bot.send_message(i.user_id, "Поступил новый заказ!")
                except Exception as e:
                    await log_exception(e)
    else:
        await query.message.answer("Оплата не прошла, возможно стоит подождать")


def register_order_handlers(dp):
    dp.register_callback_query_handler(
        subject_callback_handler,
        lambda c: c.data.startswith("subject-")
    )
    dp.register_callback_query_handler(
        order_type_callback_handler,
        lambda c: c.data.startswith("order_type-"),
        state=OrderStates.waiting_for_order_type
    )
    dp.register_message_handler(
        process_order_details,
        state=OrderStates.waiting_for_order_details
    )
    dp.register_message_handler(
        handle_order_files,
        content_types=[ContentType.DOCUMENT, ContentType.PHOTO],
        state=OrderStates.waiting_for_files
    )
    dp.register_callback_query_handler(
        finish_files_handler,
        lambda c: c.data == "finish_files",
        state=OrderStates.waiting_for_files
    )
    dp.register_callback_query_handler(
        check_balance,
        lambda c: c.data == "check-balance",
        state=OrderStates.waiting_for_pay
    )

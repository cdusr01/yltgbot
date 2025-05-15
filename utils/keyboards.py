from service.order_types_service import OrderTypeService
from service.role_service import RoleService
from service.subject_service import SubjectService

subject_service = SubjectService()
order_type_service = OrderTypeService()
role_service = RoleService()

def get_subjects_keyboard():
    """Клавиатура с предметами"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    for subject in subject_service.get_all():
        keyboard.add(InlineKeyboardButton(
            text=subject.name,
            callback_data=f"subject-{subject.id}"
        ))
    return keyboard

def get_order_types_keyboard(subject_id):
    """Клавиатура с типами заказов"""
    keyboard = InlineKeyboardMarkup()
    for order_type in order_type_service.get_all_by_subject(subject_id):
        keyboard.add(InlineKeyboardButton(
            text=order_type.name,
            callback_data=f"order_type-{order_type.id}"
        ))
    keyboard.add(get_cancel_button())
    return keyboard

def get_admin_keyboard():
    """Клавиатура админ-панели"""
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("Список пользователей", callback_data="get-all-users"),
        InlineKeyboardButton("Назначить роль", callback_data="set_role")
    )

def get_cancel_keyboard():
    """Кнопка отмены"""
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("Отмена", callback_data="cancel")
    )


def get_cancel_button():
    return InlineKeyboardButton(text="Отмена", callback_data="cancel")


def get_roles_keyboard():
    """Клавиатура с ролями"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    for role in role_service.get_all():
        keyboard.add(InlineKeyboardButton(
            text=role.type,
            callback_data=f"role-{role.id}"
        ))
    keyboard.add(get_cancel_button())
    return keyboard


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_orders_list_keyboard(orders):
    """Клавиатура со списком заказов"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    for order in orders:
        keyboard.add(
            InlineKeyboardButton(
                text=f"Заказ #{order.id}",
                callback_data=f"view_order-{order.id}"
            )
        )
    return keyboard


def get_order_actions_keyboard(order, user):
    """Клавиатура с действиями для заказа"""
    keyboard = InlineKeyboardMarkup()

    if not order.freelancer_id:  # Если заказ ещё не принят
        if user.role_id < 5:  # Только для исполнителей
            keyboard.add(
                InlineKeyboardButton(
                    text="✅ Принять заказ",
                    callback_data=f"accept_order-{order.id}"
                )
            )

    keyboard.add(
        InlineKeyboardButton(
            text="🔙 Назад к списку",
            callback_data="back_to_orders"
        )
    )

    return keyboard

def get_cancel_order_button():
    return InlineKeyboardButton(text="Отменить заказ", callback_data="cancel-order")


def get_to_pay_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Поплнить счёт", callback_data="update-balance"))
    return keyboard

def get_payment_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Проверить пополнения", callback_data="check-balance"))
    return keyboard
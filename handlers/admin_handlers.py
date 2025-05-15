from aiogram import types
from aiogram.dispatcher import FSMContext

from service.role_service import RoleService
from service.user_service import UserService
from states.role_states import RoleStates
from utils.logger import log_interaction

from utils.keyboards import get_cancel_keyboard, get_admin_keyboard, get_roles_keyboard

user_service = UserService()
role_service = RoleService()


async def admin_panel_handler(message: types.Message):
    """Обработчик админ-панели"""
    if not str(message.from_user.id) in list(map(lambda x: x.user_id, user_service.get_all_admins())):
        return

    await message.answer(
        "Админ-панель:",
        reply_markup=get_admin_keyboard()
    )
    await log_interaction(f"Admin {message.from_user.id} accessed panel")


async def show_users_list(callback: types.CallbackQuery):
    """Показать список пользователей"""
    users = user_service.get_all()
    await callback.message.edit_text(
        f"Всего пользователей: {len(users)}\n" +
        "\n".join([f"{u.user_id} - @{u.user_tag}" for u in users])
    )
    await log_interaction(f"Admin {callback.from_user.id} viewed users list")


async def set_role_handler(callback: types.CallbackQuery):
    """Начать процесс назначения роли"""
    await RoleStates.waiting_for_user_id.set()
    await callback.message.edit_text(
        "Введите ID пользователя или @username:",
        reply_markup=get_cancel_keyboard()
    )


async def process_user_id(message: types.Message, state: FSMContext):
    """Обработка ID пользователя для назначения роли"""
    user_identifier = message.text.strip().replace("@", "").replace("https://t.me/", "")
    if user_identifier.isdigit():
        user = user_service.get_by_user_id(int(user_identifier))
    else:
        user = user_service.get_by_username(user_identifier)

    if not user:
        await message.answer("Пользователь не найден!")
        await state.finish()
        return

    await state.update_data(user_id=user.user_id)
    await RoleStates.next()
    await message.answer(
        "Выберите роль:",
        reply_markup=get_roles_keyboard()
    )


async def process_role_selection(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора роли"""
    role_id = int(callback.data.split("-")[1])
    data = await state.get_data()

    user = user_service.get_by_user_id(data['user_id'])
    user.role_id = role_id
    user_service.update(user)

    await callback.message.edit_text(
        f"Пользователю @{user.user_tag} назначена роль {role_service.get_by_id(role_id).type}"
    )
    await state.finish()
    await log_interaction(f"Admin {callback.from_user.id} changed role for {user.user_id}")


def register_admin_handlers(dp):
    dp.register_message_handler(
        admin_panel_handler,
        commands=["adminpanel"]
    )
    dp.register_callback_query_handler(
        show_users_list,
        lambda c: c.data == "get-all-users"
    )
    dp.register_callback_query_handler(
        set_role_handler,
        lambda c: c.data == "set_role"
    )
    dp.register_message_handler(
        process_user_id,
        state=RoleStates.waiting_for_user_id
    )
    dp.register_callback_query_handler(
        process_role_selection,
        lambda c: c.data.startswith("role-"),
        state=RoleStates.waiting_for_role_number
    )
from aiogram import types
from aiogram.dispatcher import FSMContext
from utils.logger import log_interaction, log_exception


async def cancel_handler(callback_query: types.CallbackQuery, state: FSMContext):
    """Универсальный обработчик кнопки 'Отмена'"""
    try:
        await callback_query.answer("Действие отменено")
        await callback_query.message.edit_text("❌ Действие отменено")
        await state.finish()
        await log_interaction(f"User {callback_query.from_user.id} cancelled action")
    except Exception as e:
        await log_exception(e, "cancel_handler")


async def cancel_command_handler(message: types.Message, state: FSMContext):
    """Универсальный обработчик кнопки 'Отмена'"""
    try:
        await message.answer("❌ Отменено")
        await state.finish()
        await log_interaction(f"User {message.from_user.id} cancelled action (/cancel)")
    except Exception as e:
        await log_exception(e, "cancel_command_handler")

def register_common_handlers(dp):
    dp.register_callback_query_handler(
        cancel_handler,
        lambda c: c.data == "cancel",
        state="*"  # Обрабатывает отмену в любом состоянии
    )
    dp.register_message_handler(
        cancel_command_handler,
        commands=["cancel"],
        state="*"
    )
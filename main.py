from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.files import JSONStorage
from aiogram.utils.json import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import json

import config
from handlers.common_handlers import register_common_handlers
from handlers.admin_handlers import register_admin_handlers
from handlers.order_handlers import register_order_handlers
from handlers.order_managment_handlers import register_order_management_handlers
from handlers.user_handlers import register_user_handlers

from utils.logger import setup_logging


async def on_startup(dp):
    """Действия при запуске бота"""
    scheduler = AsyncIOScheduler()
    scheduler.start()
    setup_logging()
    # Дополнительная инициализация


def main():
    """Основная функция"""
    try:
        storage = JSONStorage(path='bot_states.json')
    except json.decoder.JSONDecodeError:
        s = open('bot_states.json', 'w')
        s.write("{}")
        s.close()
        storage = JSONStorage(path='bot_states.json')
    bot = Bot(token=config.TOKEN, parse_mode="HTML")
    dp = Dispatcher(bot, storage=storage)

    # Регистрация обработчиков
    register_user_handlers(dp)
    register_order_handlers(dp)
    register_admin_handlers(dp)
    register_common_handlers(dp)
    register_order_management_handlers(dp)

    # Запуск поллинга
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


if __name__ == "__main__":
    main()
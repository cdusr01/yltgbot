import logging
import datetime
from typing import Optional
from pathlib import Path


# Настройка базовой конфигурации логирования
def setup_logging():
    """Инициализация системы логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(),  # Вывод в консоль
            logging.FileHandler("logs/bot.log")  # Основной лог-файл
        ]
    )
    _ensure_logs_directory()
    _schedule_log_rotation()


def _ensure_logs_directory():
    """Создает директорию для логов, если её нет"""
    Path("logs").mkdir(exist_ok=True)


def _schedule_log_rotation():
    """Планирует ротацию логов (если используете APScheduler)"""
    # Можно добавить при необходимости
    pass


async def log_interaction(message: str, user_id: Optional[int] = None):
    """
    Логирование действий пользователя
    :param message: Сообщение для логирования
    :param user_id: ID пользователя (опционально)
    """
    log_msg = f"[USER {user_id}] {message}" if user_id else message
    logging.info(log_msg)
    await _write_to_daily_log(log_msg)


async def log_exception(error: Exception, context: Optional[str] = None):
    """
    Логирование исключений
    :param error: Объект исключения
    :param context: Контекст возникновения ошибки
    """
    error_msg = f"ERROR: {str(error)}"
    if context:
        error_msg = f"[{context}] {error_msg}"

    logging.error(error_msg, exc_info=True)
    await _write_to_daily_log(error_msg, is_error=True)


async def _write_to_daily_log(message: str, is_error: bool = False):
    """
    Запись в дневной лог-файл
    :param message: Сообщение для записи
    :param is_error: Флаг ошибки (запись в отдельный файл)
    """
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    log_type = "exception" if is_error else "log"
    log_file = f"logs/{current_date}-{log_type}.txt"

    try:
        with open(log_file, "a", encoding="UTF-8") as f:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            f.write(f"{timestamp}#{message}\n")
    except Exception as e:
        logging.error(f"Failed to write to log file: {str(e)}")


async def create_daily_log_files():
    """
    Создает файлы для логирования на текущий день
    Вызывается при старте бота и по расписанию
    """
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    files = {
        f"logs/{current_date}-log.txt",
        f"logs/{current_date}-exception.txt"
    }

    for file in files:
        try:
            with open(file, "a", encoding="UTF-8"):
                pass  # Просто создаем файл если не существует
        except Exception as e:
            logging.error(f"Failed to create log file {file}: {str(e)}")


# Декоратор для логирования функций
def log_execution(func):
    async def wrapper(*args, **kwargs):
        try:
            logging.info(f"Executing {func.__name__}")
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            await log_exception(e, f"in {func.__name__}")
            raise

    return wrapper
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
import asyncio

import handlers
import database

API_TOKEN = '8831733049:AAEUWa--e3jXVTyylabUKr8GEffOodqL9wM'

# Создаём экземпляр бота с своим токеном
bot = Bot(token=API_TOKEN)
# Инициализируем хранилище состояний (FSM) в оперативной памяти.
# Оно нужно, чтобы помнить, на каком шаге находится пользователь (например, «ждём ссылку»).
storage = MemoryStorage()
# Создаём диспетчер (главный объект, который управляет всеми обновлениями от Telegram)
dp = Dispatcher(bot, storage=storage)


# Регистрация хендлеров (обработчиков событий)

# Обработчик команды /start — приветствие и главное меню
dp.register_message_handler(handlers.send_welcome, commands=['start'])
# Обработка нажатия кнопки «Загрузить файл» из главного меню
dp.register_message_handler(handlers.download_file_start, lambda m: m.text == 'Загрузить файл')
# Обработка кнопки «Отмена» (только когда пользователь в состоянии ожидания URL)
dp.register_callback_query_handler(
    handlers.process_cancel,
    lambda c: c.data == 'cancel_download',
    state=handlers.DownloadFileStates.waiting_for_url
)
# Обработка присланной ссылки (только когда пользователь в состоянии ожидания URL)
dp.register_message_handler(handlers.process_url, state=handlers.DownloadFileStates.waiting_for_url)
# Обработчики команды /help и кнопки «Помощь
dp.register_message_handler(handlers.send_help, commands=['help'])
dp.register_message_handler(handlers.send_help, lambda m: m.text == 'Помощь')
# Обработчик кнопки «О боте»
dp.register_message_handler(handlers.about_bot, lambda m: m.text == 'О боте')
# Обработчики инлайн-кнопок «Показать историю» и «Очистить историю»
dp.register_callback_query_handler(handlers.show_history, lambda c: c.data == 'show_history')
dp.register_callback_query_handler(handlers.clear_history, lambda c: c.data == 'clear_history')
dp.register_message_handler(handlers.handle_errors)

async def on_startup(dp):
    await database.init_db()

if __name__ == '__main__':
    print("Бот запускается...")
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

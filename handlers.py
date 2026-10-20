import os
import aiofiles
import aiohttp
from typing import Optional
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiofiles import os as aiofiles_os

from keyboards import get_main_keyboard, get_cancel_button, get_history_buttons
from database import add_download, get_user_history, clear_user_history
from aiogram.dispatcher.filters.state import State, StatesGroup


#Cостояние, когда бот ждёт от пользователя URL для скачивания.
class DownloadFileStates(StatesGroup):
    waiting_for_url = State()

#Обработчик команды /start.
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот для загрузки файлов по URL.", reply_markup=get_main_keyboard())

#Запускает процесс загрузки: переводит бота в состояние ожидания URL
async def download_file_start(message: types.Message):
    await DownloadFileStates.waiting_for_url.set()
    await message.answer(
        "Отправьте мне прямую ссылку на файл (должна начинаться с http:// или https://).",
        reply_markup=get_cancel_button()
    )

# Обрабатывает нажатие кнопки «Отмена».
async def process_cancel(callback_query: types.CallbackQuery, state: FSMContext):
    print("[LOG] Отмена загрузки")
    await callback_query.answer()
    await state.finish()
    await callback_query.message.answer(
        "✅ Загрузка отменена. Выберите действие в меню:",
        reply_markup=get_main_keyboard()
    )

# Основной обработчик: принимает URL от пользователя, скачивает файл и отправляет его в чат.
# Также сохраняет ссылку в базу данных истории.
async def process_url(message: types.Message, state: FSMContext):
    url = message.text.strip()
    user_id = message.from_user.id

    if not url.startswith(("http://", "https://")):
        await message.answer("Пожалуйста, пришлите корректный URL (начинается с http:// или https://).")
        return

    try:
        # Создаём сессию с таймаутом 60 секунд, чтобы бот не висел бесконечно
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Делаем GET-запрос с автоматическим следованием редиректам
            async with session.get(url, allow_redirects=True) as response:
                # Если сервер не вернул 200 OK — это уже ошибка скачивания
                if response.status != 200:
                    await message.answer(f"Не удалось загрузить файл. HTTP статус: {response.status}")
                    await state.finish()
                    return

                content_type = response.headers.get('Content-Type', '')
                # Простая защита: если вместо файла пришёл HTML — скорее всего, это страница, а не файл
                if content_type.startswith('text/html'):
                    await message.answer("Ссылка ведёт на страницу, а не на файл. Нужна прямая ссылка на скачивание.")
                    await state.finish()
                    return

                # Проверка размера файла по заголовку Content-Length
                content_length = response.headers.get('Content-Length')
                if content_length:
                    size_mb = int(content_length) / (1024 * 1024)
                    if size_mb > 50:
                        await message.answer(f"Файл слишком большой ({size_mb:.1f} МБ). Лимит Telegram: 50 МБ.")
                        await state.finish()
                        return

                file_name = os.path.basename(url)
                # Если имя пустое или содержит слэш — ставим заглушку
                if not file_name or '/' in file_name:
                    file_name = 'downloaded_file'

                async with aiofiles.open(file_name, 'wb') as f:
                    await f.write(await response.read())

                size = os.path.getsize(file_name)
                print(f"[LOG] Скачано {size} байт")

                with open(file_name, 'rb') as file:
                    await message.answer_document(file, caption="✅ Файл успешно загружен!")

                await aiofiles_os.remove(file_name)

                # Сохраняем в БД именно для этого пользователя
                await add_download(user_id, url)

    except Exception as e:
        print(f"[ERROR] {e}")
        await message.answer(f"Произошла ошибка: {e}")

    finally:
        await state.finish()

# Отправляет инструкцию по использованию бота и кнопки управления историей.
async def send_help(message: types.Message):
    text = (
        "Инструкция:\n\n"
        "1. Нажмите «Загрузить файл».\n"
        "2. Отправьте прямую ссылку на файл.\n"
        "3. Получите файл в чате.\n\n"
        "История загрузок хранится персонально для каждого пользователя."
    )
    await message.answer(text, reply_markup=get_history_buttons())

# Отправляет краткую информацию о версии и функционале бота.
async def about_bot(message: types.Message):
    await message.answer("Бот версии 1.1. Загрузка файлов по прямой ссылке + персональная история.")

#Показывает пользователю его персональную историю загрузок (последние 10 ссылок)
async def show_history(callback_query: types.CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    history = await get_user_history(user_id, limit=10)

    if not history:
        await callback_query.message.answer("Ваша история загрузок пуста.")
        return

    history_text = "Ваша история загрузок (последние 10):\n\n"
    for i, (url, timestamp) in enumerate(history, 1):
        history_text += f"{i}. {url}"

    await callback_query.message.answer(history_text)

#Очищает персональную историю загрузок только для текущего пользователя.
async def clear_history(callback_query: types.CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    await clear_user_history(user_id)
    await callback_query.message.answer("✅ Ваша история очищена.")

#Универсальный обработчик для непонятных сообщений.
async def handle_errors(message: types.Message):
    await message.reply("Я не понял вашего сообщения. Используйте кнопки меню.")

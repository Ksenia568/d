from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


#Создаёт кнопки главного меню бота (обычные кнопки внизу экрана).
def get_main_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('Загрузить файл'))
    kb.add(KeyboardButton('Помощь'))
    kb.add(KeyboardButton('О боте'))
    return kb

#Это инлайн-кнопка (появляется над сообщением), чтобы пользователь мог отменить процесс загрузки, не выходя в главное меню.
def get_cancel_button():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton('❌ Отмена', callback_data='cancel_download'))
    return kb

# Кнопки управления историей загрузок (показать / очистить).
def get_history_buttons():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton('📜 Показать историю', callback_data='show_history'),
        InlineKeyboardButton('🗑️ Очистить историю', callback_data='clear_history'),
    )
    return kb
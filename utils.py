# utils.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

def main_menu_keyboard():
    """Inline-клавиатура для основного меню."""
    keyboard = [
        [InlineKeyboardButton("Создать заявку", callback_data='create_order')],
        [InlineKeyboardButton("Баланс", callback_data='balance')],
        [InlineKeyboardButton("О нас", callback_data='about')]
    ]
    return InlineKeyboardMarkup(keyboard)

def bank_keyboard():
    keyboard = [
        [InlineKeyboardButton("Банк 1", callback_data='bank_1')],
        [InlineKeyboardButton("Банк 2", callback_data='bank_2')],
        [InlineKeyboardButton("Банк 3", callback_data='bank_3')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def time_keyboard():
    keyboard = [
        [InlineKeyboardButton("15 минут", callback_data='time_15')],
        [InlineKeyboardButton("30 минут", callback_data='time_30')],
        [InlineKeyboardButton("45 минут", callback_data='time_45')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def balance_keyboard():
    keyboard = [
        [InlineKeyboardButton("Вывод через адрес", callback_data='withdraw_address')],
        [InlineKeyboardButton("Вывод через чек криптобота", callback_data='withdraw_cheque')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def reply_commands_keyboard(is_admin=False):
    """
    Reply‑клавиатура, которая всегда видна внизу чата.
    Для обычных пользователей – кнопки "Главное меню" и "Поддержка",
    для администратора – "Главное меню" и "Отправить сообщение".
    """
    if is_admin:
        keyboard = [["Главное меню", "Отправить сообщение"]]
    else:
        keyboard = [["Главное меню", "Поддержка"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

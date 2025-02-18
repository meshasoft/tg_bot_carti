# handlers.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, BotCommandScopeChat
from telegram.ext import ContextTypes, ConversationHandler
from config import ADMIN_CHAT_ID
from utils import main_menu_keyboard, bank_keyboard, time_keyboard, balance_keyboard, reply_commands_keyboard

# Глобальное временное хранилище заявок (для демонстрации)
orders = {}

# Состояние для диалога поддержки
SUPPORT = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Команда /start – отправляет приветственное сообщение с reply‑клавиатурой
    и программно устанавливает для данного чата список доступных команд.
    """
    user_id = update.effective_user.id
    if user_id == ADMIN_CHAT_ID:
        commands = [
            BotCommand("start", "Запустить бота"),
            BotCommand("send", "Отправить сообщение пользователю"),
            BotCommand("cancel", "Отменить операцию")
        ]
    else:
        commands = [
            BotCommand("start", "Запустить бота"),
            BotCommand("help", "Поддержка: задать вопрос")
        ]
    # Устанавливаем команды для данного чата (в private-чате chat_id = user_id)
    await context.bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=user_id))
    
    is_admin = (user_id == ADMIN_CHAT_ID)
    reply_kb = reply_commands_keyboard(is_admin)
    if update.message:
        await update.message.reply_text("Добро пожаловать! Выберите действие:", reply_markup=reply_kb)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик inline‑кнопок (для заказов и навигации)."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == 'back_to_main':
        await query.edit_message_text("Главное меню:", reply_markup=main_menu_keyboard())
        return

    if data == 'create_order':
        await query.edit_message_text("Выберите банк:", reply_markup=bank_keyboard())

    elif data in ['bank_1', 'bank_2', 'bank_3']:
        orders[user_id] = {'bank': data}
        await query.edit_message_text("Выберите срок оплаты:", reply_markup=time_keyboard())

    elif data in ['time_15', 'time_30', 'time_45']:
        if user_id in orders:
            orders[user_id]['time'] = data
            order_details = (
                f"Новая заявка от {query.from_user.full_name} (ID: <code>{user_id}</code>).\n"
                f"Банк: {orders[user_id]['bank']}\n"
                f"Срок оплаты: {data.replace('time_', '')} минут"
            )
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=order_details,
                parse_mode="HTML"
            )
            await query.edit_message_text(
                "Ваша заявка отправлена на обработку. Ожидайте уведомления.",
                reply_markup=main_menu_keyboard()
            )
        else:
            await query.edit_message_text("Ошибка: заявка не найдена.", reply_markup=main_menu_keyboard())

    elif data == 'balance':
        balance = orders.get(user_id, {}).get('balance', 0)
        await query.edit_message_text(f"Ваш баланс: {balance} руб.", reply_markup=balance_keyboard())

    elif data == 'about':
        text = "Это быстрый и удобный бот для обработки заявок. Подробности на нашем новостном канале."
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Новостной канал", url="https://t.me/your_channel")],
            [InlineKeyboardButton("Назад", callback_data='back_to_main')]
        ])
        await query.edit_message_text(text, reply_markup=reply_markup)

    elif data == 'withdraw_address':
        await query.edit_message_text(
            "Пожалуйста, отправьте ваш TRC20 адрес в ответном сообщении.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='back_to_main')]])
        )
    elif data == 'withdraw_cheque':
        await query.edit_message_text(
            "Функция вывода через чек криптобота пока недоступна.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='back_to_main')]])
        )
    else:
        await query.edit_message_text("Неизвестная команда.", reply_markup=main_menu_keyboard())

async def support_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Entry point для поддержки.
    Если обычный пользователь инициирует поддержку (через кнопку "Поддержка" или /help),
    бот запрашивает вопрос, который будет отправлен админу.
    Для администратора эта команда недоступна.
    """
    if update.effective_user.id == ADMIN_CHAT_ID:
        await update.message.reply_text("Эта команда недоступна для администратора.")
        return ConversationHandler.END
    await update.message.reply_text(
        "Пожалуйста, напишите ваш вопрос для поддержки, и он будет отправлен администратору."
    )
    return SUPPORT

async def support_receive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Получает текст вопроса поддержки от пользователя и пересылает его админу.
    """
    if update.message and update.message.text:
        question = update.message.text
        user_id = update.effective_user.id
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"Вопрос от пользователя <code>{user_id}</code>:\n{question}",
                parse_mode="HTML"
            )
            await update.message.reply_text("Ваш вопрос отправлен в поддержку. Ожидайте ответа.")
        except Exception as e:
            await update.message.reply_text(f"Ошибка при отправке: {e}")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Команда отмены поддержки."""
    await update.message.reply_text("Поддержка отменена.")
    return ConversationHandler.END

async def admin_send_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /send для администратора: отправка сообщения пользователю."""
    if update.effective_chat.id != ADMIN_CHAT_ID:
        await update.message.reply_text("У вас нет прав на эту команду.")
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Использование: /send <user_id> <сообщение>")
        return

    user_id_str = args[0]
    message_text = " ".join(args[1:])
    try:
        user_id_int = int(user_id_str)
    except ValueError:
        await update.message.reply_text("Некорректный user_id. Должен быть числом.")
        return

    try:
        await context.bot.send_message(chat_id=user_id_int, text=message_text)
        await update.message.reply_text(f"Сообщение успешно отправлено пользователю <code>{user_id_int}</code>.",
                                          parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при отправке сообщения: {e}")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает текстовые сообщения из reply‑клавиатуры.
    Распознаёт команды "Главное меню" и "Отправить сообщение" (для администратора).
    Если сообщение не соответствует известным командам, выводит подсказку,
    с корректными вариантами для обычного пользователя и для администратора.
    """
    user_text = update.message.text
    is_admin = (update.effective_user.id == ADMIN_CHAT_ID)
    if user_text == "Главное меню":
        await update.message.reply_text("Главное меню:", reply_markup=main_menu_keyboard())
    elif user_text == "Отправить сообщение":
        if is_admin:
            await update.message.reply_text("Для отправки сообщения используйте команду:\n/send <user_id> <сообщение>")
        else:
            await update.message.reply_text("У вас нет прав на эту команду.")
    else:
        if is_admin:
            await update.message.reply_text("Неизвестная команда. Нажмите 'Главное меню' или 'Отправить сообщение'.")
        else:
            await update.message.reply_text("Неизвестная команда. Нажмите 'Главное меню' или 'Поддержка'.")

# bot.py
import asyncio
import nest_asyncio
nest_asyncio.apply()

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters
)
from config import TOKEN
from handlers import (
    start,
    button_handler,
    admin_send_message,
    text_handler,
    support_start,
    support_receive,
    cancel,
    SUPPORT
)

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send", admin_send_message))
    
    # ConversationHandler для поддержки.
    # Entry points: команда /help и сообщение "Поддержка" из reply‑клавиатуры.
    support_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("help", support_start),
            MessageHandler(filters.Regex("^Поддержка$"), support_start)
        ],
        states={
            SUPPORT: [MessageHandler(filters.ALL, support_receive)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    app.add_handler(support_conv_handler)
    
    # Обработчик inline‑кнопок
    app.add_handler(CallbackQueryHandler(
        button_handler,
        pattern="^(create_order|bank_1|bank_2|bank_3|time_15|time_30|time_45|balance|about|withdraw_address|withdraw_cheque|back_to_main)$"
    ))
    
    # Обработчик текстовых сообщений из reply‑клавиатуры
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())

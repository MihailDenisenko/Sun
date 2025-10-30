import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from dotenv import load_dotenv

# Импортируем обработчики
from handlers.catalog import handle_manual_quantity_input

from handlers.start import start, show_contacts, show_about
from handlers.catalog import (
    show_categories, handle_category_selection, show_product_details,
    select_size, select_color, select_quantity, handle_custom_quantity,
    add_to_cart, handle_manual_quantity
)
from handlers.cart import show_cart, handle_cart_actions
from handlers.order import handle_contact, handle_manual_phone, confirm_order
from keyboards.main_menu import get_main_menu_keyboard

# Импортируем конфигурацию
from config import (
    MAIN_MENU, BROWSING_CATEGORIES, VIEWING_PRODUCT,
    SELECTING_SIZE, SELECTING_COLOR, SELECTING_QUANTITY,
    VIEWING_CART, AWAITING_PHONE, BOT_TOKEN
)

def main():
    """Главная функция запуска бота"""
    # Загружаем переменные окружения
    load_dotenv()
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Глобальные обработчики для главного меню (работают в любом состоянии)
    application.add_handler(MessageHandler(filters.Regex('^🛍️ Каталог товаров$'), show_categories))
    application.add_handler(MessageHandler(filters.Regex('^🛒 Корзина$'), show_cart))
    application.add_handler(MessageHandler(filters.Regex('^📞 Контакты$'), show_contacts))
    application.add_handler(MessageHandler(filters.Regex('^ℹ️ О магазине$'), show_about))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_manual_quantity_input))
    # ГЛОБАЛЬНЫЕ обработчики для callback-запросов (работают в любом состоянии)
    application.add_handler(CallbackQueryHandler(handle_category_selection, pattern="^cat_"))
    application.add_handler(CallbackQueryHandler(handle_category_selection, pattern="^back_to"))
    application.add_handler(CallbackQueryHandler(show_product_details, pattern="^prod_"))
    application.add_handler(CallbackQueryHandler(select_size, pattern="^select_size_"))
    application.add_handler(CallbackQueryHandler(select_color, pattern="^size_"))
    application.add_handler(CallbackQueryHandler(select_quantity, pattern="^color_"))
    application.add_handler(CallbackQueryHandler(handle_custom_quantity, pattern="^custom_qty_"))
    application.add_handler(CallbackQueryHandler(add_to_cart, pattern="^qty_"))
    application.add_handler(CallbackQueryHandler(handle_cart_actions, pattern="^(checkout|clear_cart|back_to_main)$"))
    
    # Создаем ConversationHandler только для текстовых сообщений
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [],
            BROWSING_CATEGORIES: [],
            VIEWING_PRODUCT: [],
            SELECTING_SIZE: [],
            SELECTING_COLOR: [],
            SELECTING_QUANTITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_manual_quantity)
            ],
            VIEWING_CART: [],
            AWAITING_PHONE: [
                MessageHandler(filters.CONTACT, handle_contact),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_manual_phone)
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    
    # Добавляем обработчики в приложение
    application.add_handler(conv_handler)
    
    # Обработчик для любых текстовых сообщений
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_unknown_message
    ))
    
    # Запускаем бота
    print("🤖 Бот запущен...")
    application.run_polling()


async def handle_unknown_message(update: Update, context):
    """Обрабатывает неизвестные сообщения"""
    await update.message.reply_text(
        "🤔 Я не понял ваше сообщение. Используйте кнопки меню или команду /start",
        reply_markup=get_main_menu_keyboard()
    )

if __name__ == '__main__':
    main()
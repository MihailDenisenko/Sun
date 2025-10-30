from telegram import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu_keyboard():
    """Клавиатура главного меню"""
    keyboard = [
        ['🛍️ Каталог товаров'],
        ['🛒 Корзина', '📞 Контакты'],
        ['ℹ️ О магазине']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_contact_keyboard():
    """Клавиатура для запроса контакта"""
    keyboard = [[KeyboardButton("📱 Отправить контакт", request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
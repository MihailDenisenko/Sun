from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from utils.helpers import load_products, get_categories, get_products_by_category, format_price
from keyboards.main_menu import get_main_menu_keyboard
from config import (
    MAIN_MENU, BROWSING_CATEGORIES, VIEWING_PRODUCT, 
    SELECTING_SIZE, SELECTING_COLOR, SELECTING_QUANTITY
)

# Загружаем продукты при старте с отладкой
products_data = load_products()
print(f"🎯 Загружено товаров: {len(products_data)}")
print(f"🎯 Ключи товаров: {list(products_data.keys())}")

print("🔍 Проверяем обработчики категорий...")
categories = get_categories(products_data)
for category in categories:
    print(f"🎯 Категория: {category} -> callback_data: cat_{category}")

async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает категории товаров"""
    print("🔍 Показываем категории...")
    categories = get_categories(products_data)
    
    print(f"🎯 Найдено категорий: {categories}")
    
    if not categories:
        await update.message.reply_text(
            "😔 Каталог товаров временно пуст",
            reply_markup=get_main_menu_keyboard()
        )
        return MAIN_MENU
    
    # Создаем клавиатуру с категориями
    keyboard = []
    for category in categories:
        # Преобразуем технические названия в читаемые
        category_name = get_category_display_name(category)
        keyboard.append([InlineKeyboardButton(category_name, callback_data=f"cat_{category}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")])
    
    await update.message.reply_text(
        "🎽 *Выберите категорию:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    return BROWSING_CATEGORIES

async def handle_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор категории"""
    query = update.callback_query
    await query.answer()
    
    print(f"🔍 Получен callback_data: {query.data}")
    print(f"🔍 Тип данных: {type(query.data)}")
    
    if query.data == "back_to_main":
        print("🔍 Нажата кнопка 'Назад'")
        await query.edit_message_text(
            "Возвращаемся в главное меню...",
            reply_markup=get_main_menu_keyboard()
        )
        return MAIN_MENU
    
    # Проверим что именно приходит в данных
    if query.data.startswith("cat_"):
        category = query.data.replace("cat_", "")
        print(f"🔍 Выбрана категория: '{category}'")
    else:
        print(f"🔍 Неизвестный callback_data: {query.data}")
        await query.edit_message_text(
            "❌ Ошибка выбора категории",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_categories")]])
        )
        return BROWSING_CATEGORIES
    
    category_products = get_products_by_category(products_data, category)
    
    print(f"🎯 Товары в категории '{category}': {list(category_products.keys())}")
    
    if not category_products:
        await query.edit_message_text(
            "😔 В этой категории пока нет товаров",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_categories")]])
        )
        return BROWSING_CATEGORIES
    
    # Создаем клавиатуру с товарами категории
    keyboard = []
    for product_key, product_data in category_products.items():
        product_name = product_data['name']
        product_price = format_price(product_data['price'])
        button_text = f"{product_name} - {product_price}"
        print(f"🎯 Создаем кнопку: {button_text} -> prod_{product_key}")
        keyboard.append([
            InlineKeyboardButton(button_text, callback_data=f"prod_{product_key}")
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад к категориям", callback_data="back_to_categories")])
    
    category_name = get_category_display_name(category)
    await query.edit_message_text(
        f"🛍️ *{category_name}*\n\nВыберите товар:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    return VIEWING_PRODUCT

async def show_product_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает детали товара"""
    query = update.callback_query
    await query.answer()
    
    print(f"🔍 Выбран товар: {query.data}")
    
    if query.data == "back_to_categories":
        # Возвращаемся к списку категорий
        categories = get_categories(products_data)
        keyboard = []
        for category in categories:
            category_name = get_category_display_name(category)
            keyboard.append([InlineKeyboardButton(category_name, callback_data=f"cat_{category}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")])
        
        await query.edit_message_text(
            "🎽 *Выберите категорию:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return BROWSING_CATEGORIES
    
    product_key = query.data.replace("prod_", "")
    product = products_data.get(product_key)
    
    print(f"🎯 Поиск товара по ключу: '{product_key}'")
    print(f"🎯 Найден товар: {product is not None}")
    
    if not product:
        await query.edit_message_text(
            "❌ Товар не найден",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_categories")]])
        )
        return BROWSING_CATEGORIES
    
    # Формируем сообщение с информацией о товаре
    message = f"""
🎽 *{product['name']}*

💵 *Цена:* {format_price(product['price'])}
📝 *Описание:* {product['description']}

🎨 *Доступные цвета:* {', '.join(product['colors'])}
📏 *Размеры:* {', '.join(product['sizes'])}

Выберите действие:
    """
    
    # Клавиатура действий с товаром
    keyboard = [
        [InlineKeyboardButton("📏 Выбрать размер", callback_data=f"select_size_{product_key}")],
        [InlineKeyboardButton("🔙 Назад к категории", callback_data=f"cat_{product['category']}")]
    ]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    # Сохраняем текущий товар в контексте
    context.user_data['current_product'] = product_key
    context.user_data['current_product_data'] = product
    
    return VIEWING_PRODUCT

async def select_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора размера"""
    query = update.callback_query
    await query.answer()
    
    product_key = query.data.replace("select_size_", "")
    product = products_data.get(product_key)
    
    if not product:
        await query.edit_message_text("❌ Товар не найден")
        return MAIN_MENU
    
    # Создаем клавиатуру с доступными размерами
    keyboard = []
    for size in product['sizes']:
        keyboard.append([InlineKeyboardButton(f"📏 {size}", callback_data=f"size_{product_key}_{size}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад к товару", callback_data=f"prod_{product_key}")])
    
    await query.edit_message_text(
        f"🎽 *{product['name']}*\n\nВыберите размер:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    return SELECTING_SIZE

async def select_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора цвета"""
    query = update.callback_query
    await query.answer()
    
    # data format: "size_productKey_sizeName"
    _, product_key, selected_size = query.data.split('_', 2)
    product = products_data.get(product_key)
    
    if not product:
        await query.edit_message_text("❌ Товар не найден")
        return MAIN_MENU
    
    # Сохраняем выбранный размер
    context.user_data['selected_size'] = selected_size
    
    # Создаем клавиатуру с доступными цветами
    keyboard = []
    for color in product['colors']:
        keyboard.append([InlineKeyboardButton(f"🎨 {color}", callback_data=f"color_{product_key}_{color}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад к размерам", callback_data=f"select_size_{product_key}")])
    
    await query.edit_message_text(
        f"🎽 *{product['name']}*\n"
        f"📏 Размер: {selected_size}\n\n"
        f"Выберите цвет:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    return SELECTING_COLOR

async def select_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора количества"""
    query = update.callback_query
    await query.answer()
    
    # data format: "color_productKey_colorName"
    _, product_key, selected_color = query.data.split('_', 2)
    product = products_data.get(product_key)
    
    if not product:
        await query.edit_message_text("❌ Товар не найден")
        return MAIN_MENU
    
    # Сохраняем выбранный цвет и товар
    context.user_data['selected_color'] = selected_color
    context.user_data['current_product'] = product_key
    
    # Клавиатура для выбора количества
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data=f"qty_{product_key}_1"),
            InlineKeyboardButton("2", callback_data=f"qty_{product_key}_2"), 
            InlineKeyboardButton("3", callback_data=f"qty_{product_key}_3")
        ],
        [
            InlineKeyboardButton("4", callback_data=f"qty_{product_key}_4"),
            InlineKeyboardButton("5", callback_data=f"qty_{product_key}_5"),
            InlineKeyboardButton("6", callback_data=f"qty_{product_key}_6")
        ],
        [InlineKeyboardButton("✏️ Ввести другое количество", callback_data=f"custom_qty_{product_key}")],
        [InlineKeyboardButton("🔙 Назад к цветам", callback_data=f"select_size_{product_key}")]
    ]
    
    selected_size = context.user_data.get('selected_size', 'не выбран')
    
    await query.edit_message_text(
        f"🎽 *{product['name']}*\n"
        f"📏 Размер: {selected_size}\n"
        f"🎨 Цвет: {selected_color}\n"
        f"💵 Цена: {format_price(product['price'])}\n\n"
        f"Выберите количество:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    return SELECTING_QUANTITY

async def handle_custom_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает запрос на ручной ввод количества"""
    query = update.callback_query
    await query.answer()
    
    product_key = query.data.replace("custom_qty_", "")
    product = products_data.get(product_key)
    
    if not product:
        await query.edit_message_text("❌ Товар не найден")
        return MAIN_MENU
    
    context.user_data['awaiting_custom_quantity'] = True
    
    await query.edit_message_text(
        f"🎽 *{product['name']}*\n\n"
        f"Введите количество товара (число от 1 до 100):",
        parse_mode='Markdown'
    )
    
    return SELECTING_QUANTITY

async def handle_manual_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ручной ввод количества"""
    if not context.user_data.get('awaiting_custom_quantity'):
        # Если не ожидаем ввод количества, обрабатываем как неизвестное сообщение
        await update.message.reply_text(
            "Пожалуйста, используйте кнопки для выбора товара",
            reply_markup=get_main_menu_keyboard()
        )
        return MAIN_MENU
    
    try:
        quantity = int(update.message.text)
        if quantity < 1 or quantity > 100:
            await update.message.reply_text("❌ Пожалуйста, введите число от 1 до 100:")
            return SELECTING_QUANTITY
    except ValueError:
        await update.message.reply_text("❌ Пожалуйста, введите корректное число:")
        return SELECTING_QUANTITY
    
    # Получаем данные товара
    product_key = context.user_data.get('current_product')
    product = products_data.get(product_key)
    
    if not product:
        await update.message.reply_text("❌ Товар не найден")
        return MAIN_MENU
    
    # Добавляем товар в корзину
    selected_size = context.user_data.get('selected_size')
    selected_color = context.user_data.get('selected_color')
    
    cart_item = {
        'product_key': product_key,
        'name': product['name'],
        'size': selected_size,
        'color': selected_color, 
        'price': product['price'],
        'quantity': quantity,
        'total': product['price'] * quantity
    }
    
    # Инициализируем корзину если её нет
    if 'cart' not in context.user_data:
        context.user_data['cart'] = []
    
    # Добавляем товар в корзину
    context.user_data['cart'].append(cart_item)
    
    # Очищаем временные данные
    context.user_data.pop('current_product', None)
    context.user_data.pop('selected_size', None)
    context.user_data.pop('selected_color', None)
    context.user_data.pop('awaiting_custom_quantity', None)
    
    await update.message.reply_text(
        f"✅ Товар добавлен в корзину!\n\n"
        f"🎽 {product['name']}\n"
        f"📏 Размер: {selected_size}\n" 
        f"🎨 Цвет: {selected_color}\n"
        f"🔢 Количество: {quantity} шт.\n"
        f"💵 Сумма: {format_price(cart_item['total'])}",
        reply_markup=get_main_menu_keyboard()
    )
    
    return MAIN_MENU



async def handle_manual_quantity_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Глобальный обработчик ручного ввода количества"""
    if not context.user_data.get('awaiting_custom_quantity'):
        # Если не ожидаем ввод количества, обрабатываем как неизвестное сообщение
        await update.message.reply_text(
            "🤔 Я не понял ваше сообщение. Используйте кнопки меню или команду /start",
            reply_markup=get_main_menu_keyboard()
        )
        return MAIN_MENU
    
    try:
        quantity = int(update.message.text)
        if quantity < 1 or quantity > 100:
            await update.message.reply_text("❌ Пожалуйста, введите число от 1 до 100:")
            return SELECTING_QUANTITY
    except ValueError:
        await update.message.reply_text("❌ Пожалуйста, введите корректное число:")
        return SELECTING_QUANTITY
    
    # Получаем данные товара
    product_key = context.user_data.get('current_product')
    product = products_data.get(product_key)
    
    if not product:
        await update.message.reply_text("❌ Товар не найден")
        return MAIN_MENU
    
    # Добавляем товар в корзину
    selected_size = context.user_data.get('selected_size')
    selected_color = context.user_data.get('selected_color')
    
    cart_item = {
        'product_key': product_key,
        'name': product['name'],
        'size': selected_size,
        'color': selected_color, 
        'price': product['price'],
        'quantity': quantity,
        'total': product['price'] * quantity
    }
    
    # Инициализируем корзину если её нет
    if 'cart' not in context.user_data:
        context.user_data['cart'] = []
    
    # Добавляем товар в корзину
    context.user_data['cart'].append(cart_item)
    
    # Очищаем временные данные
    context.user_data.pop('current_product', None)
    context.user_data.pop('selected_size', None)
    context.user_data.pop('selected_color', None)
    context.user_data.pop('awaiting_custom_quantity', None)
    
    # Показываем подтверждение
    confirmation_text = (
        f"✅ *Товар добавлен в корзину!*\n\n"
        f"🎽 *{product['name']}*\n"
        f"📏 Размер: {selected_size}\n" 
        f"🎨 Цвет: {selected_color}\n"
        f"🔢 Количество: {quantity} шт.\n"
        f"💵 Сумма: {format_price(cart_item['total'])}\n\n"
        f"🛒 *В корзине теперь {len(context.user_data['cart'])} товар(ов)*"
    )
    
    await update.message.reply_text(
        confirmation_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='Markdown'
    )
    
    return MAIN_MENU

async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавляет товар в корзину"""
    query = update.callback_query
    await query.answer()
    
    # data format: "qty_productKey_quantity"
    _, product_key, quantity_str = query.data.split('_', 2)
    quantity = int(quantity_str)
    
    product = products_data.get(product_key)
    if not product:
        await query.edit_message_text("❌ Товар не найден")
        return MAIN_MENU
    
    # Получаем выбранные параметры
    selected_size = context.user_data.get('selected_size')
    selected_color = context.user_data.get('selected_color')
    
    # Создаем объект товара для корзины
    cart_item = {
        'product_key': product_key,
        'name': product['name'],
        'size': selected_size,
        'color': selected_color, 
        'price': product['price'],
        'quantity': quantity,
        'total': product['price'] * quantity
    }
    
    # Инициализируем корзину если её нет
    if 'cart' not in context.user_data:
        context.user_data['cart'] = []
    
    # Добавляем товар в корзину
    context.user_data['cart'].append(cart_item)
    
    # Очищаем временные данные
    context.user_data.pop('current_product', None)
    context.user_data.pop('current_product_data', None) 
    context.user_data.pop('selected_size', None)
    context.user_data.pop('selected_color', None)
    
    # Показываем подтверждение добавления в корзину
    confirmation_text = (
        f"✅ *Товар добавлен в корзину!*\n\n"
        f"🎽 *{product['name']}*\n"
        f"📏 Размер: {selected_size}\n" 
        f"🎨 Цвет: {selected_color}\n"
        f"🔢 Количество: {quantity} шт.\n"
        f"💵 Сумма: {format_price(cart_item['total'])}\n\n"
        f"🛒 *В корзине теперь {len(context.user_data['cart'])} товар(ов)*"
    )
    
    await query.edit_message_text(
        confirmation_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='Markdown'
    )
    
    return MAIN_MENU


def get_category_display_name(category_key: str) -> str:
    """Преобразует техническое название категории в читаемое"""
    category_names = {
        'headwear': '👒 Головные уборы',
        'hoodies': '🧥 Толстовки и худи', 
        'pants': '👖 Штаны и брюки',
        'masks': '😷 Маски защитные',
        'tshirts': '👕 Футболки и майки'
    }
    return category_names.get(category_key, category_key)

# Регистрация обработчиков
catalog_handlers = [
    CallbackQueryHandler(handle_category_selection, pattern="^cat_|^back_to"),
    CallbackQueryHandler(show_product_details, pattern="^prod_"),
    CallbackQueryHandler(select_size, pattern="^select_size_"),
    CallbackQueryHandler(select_color, pattern="^size_"),
    CallbackQueryHandler(select_quantity, pattern="^color_"),
    CallbackQueryHandler(handle_custom_quantity, pattern="^custom_qty_"),
    CallbackQueryHandler(add_to_cart, pattern="^qty_"),
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_manual_quantity)
]
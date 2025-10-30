from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
from utils.helpers import calculate_cart_total, format_price
from keyboards.main_menu import get_main_menu_keyboard, get_contact_keyboard
from config import MAIN_MENU, VIEWING_CART, AWAITING_PHONE

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает содержимое корзины"""
    cart = context.user_data.get('cart', [])
    
    if not cart:
        await update.message.reply_text(
            "🛒 Ваша корзина пуста",
            reply_markup=get_main_menu_keyboard()
        )
        return MAIN_MENU
    
    # Формируем сообщение с содержимым корзины
    cart_text = "🛒 *Ваша корзина:*\n\n"
    total_amount = 0
    
    for i, item in enumerate(cart, 1):
        cart_text += f"{i}. *{item['name']}*\n"
        cart_text += f"   📏 Размер: {item['size']}\n"
        cart_text += f"   🎨 Цвет: {item['color']}\n" 
        cart_text += f"   🔢 Количество: {item['quantity']} шт.\n"
        cart_text += f"   💵 Сумма: {format_price(item['total'])}\n\n"
        total_amount += item['total']
    
    cart_text += f"💰 *Общая сумма: {format_price(total_amount)}*"
    
    # Клавиатура действий с корзиной
    keyboard = [
        [InlineKeyboardButton("📞 Оформить заказ", callback_data="checkout")],
        [InlineKeyboardButton("🗑️ Очистить корзину", callback_data="clear_cart")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main")]
    ]
    
    await update.message.reply_text(
        cart_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    return VIEWING_CART

async def handle_cart_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает действия с корзиной"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_to_main":
        await query.message.reply_text(
            "Возвращаемся в главное меню...",
            reply_markup=get_main_menu_keyboard()
        )
        return MAIN_MENU
    
    elif query.data == "clear_cart":
        context.user_data['cart'] = []
        # Удаляем инлайн-сообщение и отправляем новое
        await query.message.reply_text(
            "🗑️ Корзина очищена",
            reply_markup=get_main_menu_keyboard()
        )
        await query.delete_message()
        return MAIN_MENU
    
    elif query.data == "checkout":
        cart = context.user_data.get('cart', [])
        if not cart:
            await query.message.reply_text(
                "❌ Корзина пуста",
                reply_markup=get_main_menu_keyboard()
            )
            await query.delete_message()
            return MAIN_MENU
        
        # Переходим к оформлению заказа
        total_amount = calculate_cart_total(cart)
        
        order_summary = "📋 *Подтверждение заказа:*\n\n"
        for item in cart:
            order_summary += f"• {item['name']} ({item['size']}, {item['color']}) - {item['quantity']} шт.\n"
        
        order_summary += f"\n💰 *Итого: {format_price(total_amount)}*"
        order_summary += "\n\n📱 Пожалуйста, поделитесь вашим контактом для связи:"
        
        await query.message.reply_text(
            order_summary,
            reply_markup=get_contact_keyboard(),
            parse_mode='Markdown'
        )
        await query.delete_message()
        
        return AWAITING_PHONE

# Регистрация обработчиков
cart_handlers = [
    CallbackQueryHandler(handle_cart_actions, pattern="^(checkout|clear_cart|back_to_main)$")
]
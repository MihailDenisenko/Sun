from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from utils.helpers import format_price, calculate_cart_total
from keyboards.main_menu import get_main_menu_keyboard
from config import MAIN_MENU, CONFIRMING_ORDER
# from database.models import db  # РАСКОММЕНТИРОВАТЬ когда будем использовать БД

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает получение контакта"""
    contact = update.message.contact
    user = update.effective_user
    
    if contact:
        phone_number = contact.phone_number
        # Сохраняем телефон пользователя
        context.user_data['customer_phone'] = phone_number
        context.user_data['customer_name'] = f"{user.first_name} {user.last_name or ''}".strip()
    else:
        # Если контакт не отправлен, просим ввести вручную
        await update.message.reply_text(
            "📱 Пожалуйста, введите ваш номер телефона для связи:",
            reply_markup=get_main_menu_keyboard()
        )
        return AWAITING_PHONE
    
    # Переходим к подтверждению заказа
    return await confirm_order(update, context)

async def handle_manual_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ручной ввод телефона"""
    phone_number = update.message.text
    user = update.effective_user
    
    # Простая валидация номера
    if len(phone_number) < 5:
        await update.message.reply_text(
            "❌ Пожалуйста, введите корректный номер телефона:",
            reply_markup=get_main_menu_keyboard()
        )
        return AWAITING_PHONE
    
    context.user_data['customer_phone'] = phone_number
    context.user_data['customer_name'] = f"{user.first_name} {user.last_name or ''}".strip()
    
    # Переходим к подтверждению заказа
    return await confirm_order(update, context)

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение заказа"""
    cart = context.user_data.get('cart', [])
    customer_name = context.user_data.get('customer_name', 'Не указано')
    customer_phone = context.user_data.get('customer_phone', 'Не указан')
    total_amount = calculate_cart_total(cart)
    
    # Формируем финальное подтверждение
    confirmation_text = f"""
✅ *Заказ подтвержден!*

👤 *Клиент:* {customer_name}
📱 *Телефон:* {customer_phone}

📦 *Состав заказа:*
"""
    
    for item in cart:
        confirmation_text += f"• {item['name']} ({item['size']}, {item['color']}) - {item['quantity']} шт. - {format_price(item['total'])}\n"
    
    confirmation_text += f"\n💰 *Общая сумма: {format_price(total_amount)}*"
    confirmation_text += "\n\n⏳ *Статус:* Передан менеджеру\n📞 С вами свяжутся в ближайшее время для уточнения деталей."
    
    # СОХРАНЕНИЕ В БД - РАСКОММЕНТИРОВАТЬ КОГДА БУДЕТ ГОТОВО
    """
    try:
        # Сохраняем заказ в БД
        order_id = db.save_order(
            user_id=update.effective_user.id,
            order_data=cart,
            total_amount=total_amount,
            customer_name=customer_name,
            customer_phone=customer_phone
        )
        confirmation_text += f"\n\n📋 *Номер заказа:* #{order_id}"
        
        # Отправляем уведомление администраторам
        await notify_admins(update, context, order_id, cart, total_amount, customer_name, customer_phone)
        
    except Exception as e:
        confirmation_text += "\n\n⚠️ *Примечание:* Произошла ошибка при сохранении заказа. Мы уже работаем над этим!"
    """
    
    # Временная заглушка без БД
    confirmation_text += "\n\n📋 *Номер заказа:* #0001"
    await notify_admins(update, context, 1, cart, total_amount, customer_name, customer_phone)
    
    # Очищаем корзину после успешного заказа
    context.user_data['cart'] = []
    
    await update.message.reply_text(
        confirmation_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='Markdown'
    )
    
    return MAIN_MENU

async def notify_admins(update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: int, 
                       cart: list, total_amount: float, customer_name: str, customer_phone: str):
    """Отправляет уведомление администраторам о новом заказе"""
    from config import ADMIN_IDS, BOT_TOKEN
    
    if not ADMIN_IDS:
        return
    
    notification_text = f"""
🛎 *НОВЫЙ ЗАКАЗ #{order_id}*

👤 *Клиент:* {customer_name}
📱 *Телефон:* {customer_phone}
👤 *Telegram:* @{update.effective_user.username or 'не указан'}

📦 *Состав заказа:*
"""
    
    for item in cart:
        notification_text += f"• {item['name']} ({item['size']}, {item['color']}) - {item['quantity']} шт. - {format_price(item['total'])}\n"
    
    notification_text += f"\n💰 *Общая сумма: {format_price(total_amount)}*"
    notification_text += f"\n_Заказ получен от @{update.effective_user.username or 'N/A'}_"
    
    # Отправляем уведомление всем администраторам
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=notification_text,
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Не удалось отправить уведомление администратору {admin_id}: {e}")

# Регистрация обработчиков
order_handlers = [
    MessageHandler(filters.CONTACT, handle_contact),
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_manual_phone)
]
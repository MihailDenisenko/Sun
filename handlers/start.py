from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from keyboards.main_menu import get_main_menu_keyboard
from config import MAIN_MENU

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    welcome_text = f"""
👋 Привет, {user.first_name}!

Добро пожаловать в магазин одежды "Солнышко"! 

🎽 У нас ты найдешь:
• Футболки и толстовки
• Штаны и худи
• Банданы и маски
• И многое другое!

Выбирай товары, добавляй в корзину и оформляй заказ прямо здесь! 🛒
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='Markdown'
    )
    
    return MAIN_MENU

async def show_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает контакты магазина"""
    contacts_text = """
📞 *Контакты магазина*

*Телефоны:*
• +7 (812) 702-73-41
• +7 (812) 251-87-21  
• +7 (901) 314-20-65

📍 *Адрес:*
Санкт-Петербург, Набережная Обводного Канала 223/225 литера М.

*Режим работы:*
Пн-Пт: 10:00 - 18:00
Сб: 11:00 - 16:00
Вс: выходной

*Социальные сети:*
[ВКонтакте](https://vk.com/sunshintspb)
[Instagram](https://www.instagram.com/sunshint_spb)
    """
    
    # Убираем клавиатуру при переходе в контакты
    await update.message.reply_text(
        contacts_text,
        reply_markup=None,  # Убираем клавиатуру
        parse_mode='Markdown'
    )
    
    # Показываем меню снова после показа контактов
    await update.message.reply_text(
        "Вернуться в главное меню:",
        reply_markup=get_main_menu_keyboard()
    )
    
    return MAIN_MENU

async def show_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает информацию о магазине"""
    about_text = """
🏪 *О нашем магазине*

Мы - фирма "Солнышко", работаем с 2008 года!

🎯 *Наша специализация:*
• Печать на текстиле
• Пошив одежды на заказ
• Тиснение на коже
• Продажа готовой продукции

🖨️ *Услуги печати:*
• Шелкография
• Текстильный принтер  
• Шелкотрансфер
• Печать этикеток

💪 *Наши преимущества:*
• Собственное производство
• Качественные материалы
• Быстрые сроки выполнения
• Индивидуальный подход
    """
    
    # Убираем клавиатуру при переходе в "О магазине"
    await update.message.reply_text(
        about_text,
        reply_markup=None,  # Убираем клавиатуру
        parse_mode='Markdown'
    )
    
    # Показываем меню снова после показа информации
    await update.message.reply_text(
        "Вернуться в главное меню:",
        reply_markup=get_main_menu_keyboard()
    )
    
    return MAIN_MENU

# УБИРАЕМ обработчики из этого файла - переносим их в bot.py
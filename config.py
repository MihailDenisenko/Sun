import os
from dotenv import load_dotenv

load_dotenv()

# Настройки бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

# ID администраторов для уведомлений
ADMIN_IDS = [123456789]  # Замени на свои ID

# Настройки путей
PRODUCTS_JSON_PATH = "data/products.json"
DATABASE_PATH = "database/shop_bot.db"

# Состояния для ConversationHandler
(
    MAIN_MENU,
    BROWSING_CATEGORIES,
    VIEWING_PRODUCT,
    SELECTING_SIZE,
    SELECTING_COLOR,
    SELECTING_QUANTITY,
    VIEWING_CART,
    AWAITING_PHONE,
    CONFIRMING_ORDER
) = range(9)
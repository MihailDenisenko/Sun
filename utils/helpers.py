import json
import os
from typing import Dict, Any

def load_products() -> Dict[str, Any]:
    """Загружает продукты из JSON файла"""
    try:
        file_path = 'data/products.json'
        print(f"🔍 Пытаемся загрузить JSON из: {file_path}")
        print(f"🔍 Файл существует: {os.path.exists(file_path)}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"✅ Успешно загружено {len(data)} товаров")
            return data
    except FileNotFoundError:
        print("❌ Файл products.json не найден!")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        return {}
    except Exception as e:
        print(f"❌ Неизвестная ошибка: {e}")
        return {}

def get_categories(products: Dict[str, Any]) -> list:
    """Получает список уникальных категорий"""
    categories = set()
    for product_data in products.values():
        categories.add(product_data['category'])
    result = sorted(list(categories))
    print(f"🔍 Найдены категории: {result}")
    return result

def get_products_by_category(products: Dict[str, Any], category: str) -> Dict[str, Any]:
    """Получает товары по категории"""
    result = {k: v for k, v in products.items() if v['category'] == category}
    print(f"🔍 В категории '{category}' найдено {len(result)} товаров")
    return result

def format_price(price: float) -> str:
    """Форматирует цену в красивый вид"""
    return f"{price:,.0f} руб.".replace(',', ' ')

def calculate_cart_total(cart_items: list) -> float:
    """Вычисляет общую сумму корзины"""
    return sum(item['price'] * item['quantity'] for item in cart_items)
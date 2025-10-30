"""
import sqlite3
import json
from typing import List, Dict, Any

class DatabaseManager:
    def __init__(self, db_path: str = "database/shop_bot.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        # Создаем таблицы если их нет
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица заказов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                order_data TEXT,  -- JSON с составом заказа
                total_amount REAL,
                customer_name TEXT,
                customer_phone TEXT,
                status TEXT DEFAULT 'новый',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица продуктов (если будем использовать БД вместо JSON)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                image_url TEXT,
                description TEXT,
                attributes_json TEXT,  -- colors, sizes в JSON
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_order(self, user_id: int, order_data: Dict, total_amount: float, 
                   customer_name: str, customer_phone: str) -> int:
        # Сохраняем заказ в БД
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO orders 
            (user_id, order_data, total_amount, customer_name, customer_phone)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, json.dumps(order_data), total_amount, customer_name, customer_phone))
        
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return order_id
    
    def get_user_orders(self, user_id: int) -> List[Dict]:
        # Получаем историю заказов пользователя
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, order_data, total_amount, status, created_at
            FROM orders WHERE user_id = ? ORDER BY created_at DESC
        ''', (user_id,))
        
        orders = []
        for row in cursor.fetchall():
            order_id, order_data, total_amount, status, created_at = row
            orders.append({
                'id': order_id,
                'order_data': json.loads(order_data),
                'total_amount': total_amount,
                'status': status,
                'created_at': created_at
            })
        
        conn.close()
        return orders

# Глобальный экземпляр БД
# db = DatabaseManager()
"""
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage



# Подключение к базе данных
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        coins INTEGER DEFAULT 0
    )
""")
conn.commit()



class control_db:
    # Функция для проверки регистрации пользовmessage.from_user.id
    def is_registered(user_id):
        cursor.execute("SELECT name, coins FROM users WHERE user_id = ?", (user_id,))
        return cursor.fetchone()

    # Функция для сохранения имени пользователя с начальным балансом монет
    def save_user(user_id, name):
        cursor.execute("INSERT INTO users (user_id, name, coins) VALUES (?, ?, 0)", (user_id, name))
        conn.commit()

    # Функция для начисления монет
    def add_coin(user_id, amount):
        cursor.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()

    # Функция для получения баланса пользователя
    def get_coin(user_id):
        cursor.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 0
    
    # Функция для получения имени пользователя
    def get_name(user_id):
        cursor.execute("SELECT name FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    # Функция для списания монет
    def deduct_coins(user_id, amount):
        cursor.execute("UPDATE users SET coins = coins - ? WHERE user_id = ? AND coins >= ?", (amount, user_id, amount))
        conn.commit()

    # Функция для получения места пользователя в рейтинге
    def get_user_rank(user_id):
        cursor.execute("SELECT user_id FROM users ORDER BY coins DESC")
        users = cursor.fetchall()
        for index, (uid,) in enumerate(users, start=1):
            if uid == user_id:
                return index
        return None

    # Функция для получения топ-10 пользователей по монетам
    def get_top_rank():
        cursor.execute("SELECT name, coins FROM users ORDER BY coins DESC LIMIT 10")
        top_users = cursor.fetchall()
        
        if not top_users:
            return "Рейтинг пока пуст."
        
        return "\n".join([f"{idx+1}. {name} — {coins} монет" for idx, (name, coins) in enumerate(top_users)])




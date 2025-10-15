# --- START OF FILE dbrequest.py ---

import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Единый класс для управления базой данных приложения.
    Объединяет функциональность user_login, user_data и field_data.
    """
    def __init__(self, db_path="db/app_data.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        logger.info(f"Инициализация единой базы данных: {self.db_path}")
        self._create_tables()

    def _get_connection(self):
        """Возвращает соединение с базой данных с включенными внешними ключами."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _create_tables(self):
        """Создает все необходимые таблицы в базе данных, если они не существуют."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # 1. Таблица пользователей
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        login TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        token TEXT UNIQUE,
                        first_name TEXT NOT NULL DEFAULT '',
                        last_name TEXT NOT NULL DEFAULT ''
                    )
                ''')
                # 2. Таблица с данными пользователя (JSON-строка для списков и т.д.)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_data (
                        user_id INTEGER PRIMARY KEY,
                        data TEXT,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                ''')
                # 3. Таблица для хранения полных данных анализов
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analyses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        analysis_id TEXT UNIQUE NOT NULL,
                        data TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                ''')
                # 4. Таблица для общего хранения ключ-значение (для эндпоинтов /field/...)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS generic_data (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                ''')
                conn.commit()
                logger.info(f"Все таблицы в {self.db_path} созданы/проверены.")
        except Exception as e:
            logger.error(f"Ошибка при создании таблиц: {e}")
            raise

    # --- Вспомогательные методы ---
    def _get_user_id_by_token(self, token, cursor):
        """Вспомогательная функция для получения ID пользователя по токену."""
        cursor.execute('SELECT id FROM users WHERE token = ?', (token,))
        result = cursor.fetchone()
        return result[0] if result else None

    # --- Методы для работы с пользователями (users) ---
    def add_new_user(self, login, password, token, first_name, last_name):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO users (login, password, token, first_name, last_name) VALUES (?, ?, ?, ?, ?)',
                    (login, password, token, first_name, last_name)
                )
                user_id = cursor.lastrowid
                # Сразу создаем пустую запись в user_data
                cursor.execute('INSERT INTO user_data (user_id, data) VALUES (?, ?)', (user_id, '{}'))
                conn.commit()
                logger.info(f"Пользователь {login} (ID: {user_id}) успешно добавлен.")
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"Пользователь {login} или токен уже существуют.")
            return False
        except Exception as e:
            logger.error(f"Ошибка при добавлении пользователя {login}: {e}")
            return False

    def get_token(self, login, password):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT token FROM users WHERE login = ? AND password = ?', (login, password))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Ошибка при получении токена для {login}: {e}")
            return None

    def user_exists(self, login):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM users WHERE login = ?', (login,))
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Ошибка при проверке пользователя {login}: {e}")
            return False

    def if_token_exist(self, token):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM users WHERE token = ?', (token,))
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Ошибка при проверке токена {token}: {e}")
            return False
            
    def get_user_info_by_token(self, token):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT login, first_name, last_name FROM users WHERE token = ?', (token,))
                result = cursor.fetchone()
                if result:
                    return {"login": result[0], "first_name": result[1], "last_name": result[2]}
                return None
        except Exception as e:
            logger.error(f"Ошибка при получении информации по токену {token}: {e}")
            return None
            
    def get_all_users(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT login, first_name, last_name FROM users')
                users_list = [{"login": r[0], "first_name": r[1], "last_name": r[2]} for r in cursor.fetchall()]
                return users_list
        except Exception as e:
            logger.error(f"Ошибка при получении списка всех пользователей: {e}")
            return []

    # --- Методы для данных пользователя (user_data) ---
    def get_user_data(self, token):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                user_id = self._get_user_id_by_token(token, cursor)
                if not user_id: return None
                cursor.execute('SELECT data FROM user_data WHERE user_id = ?', (user_id,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Ошибка получения данных для токена {token}: {e}")
            return None

    def save_user_data(self, token, data_str):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                user_id = self._get_user_id_by_token(token, cursor)
                if not user_id: return False
                cursor.execute(
                    'INSERT OR REPLACE INTO user_data (user_id, data) VALUES (?, ?)',
                    (user_id, data_str)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка сохранения данных для токена {token}: {e}")
            return False

    # --- Методы для данных анализов (analyses) ---
    def save_analysis_data(self, token, analysis_id, data_str):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                user_id = self._get_user_id_by_token(token, cursor)
                if not user_id: return False
                cursor.execute(
                    'INSERT OR REPLACE INTO analyses (user_id, analysis_id, data) VALUES (?, ?, ?)',
                    (user_id, analysis_id, data_str)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка сохранения анализа {analysis_id}: {e}")
            return False
            
    def get_analysis_data(self, token, analysis_id):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                user_id = self._get_user_id_by_token(token, cursor)
                if not user_id: return None
                cursor.execute('SELECT data FROM analyses WHERE user_id = ? AND analysis_id = ?', (user_id, analysis_id))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Ошибка получения анализа {analysis_id}: {e}")
            return None

    def delete_analysis_data(self, token, analysis_id):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                user_id = self._get_user_id_by_token(token, cursor)
                if not user_id: return False
                cursor.execute('DELETE FROM analyses WHERE user_id = ? AND analysis_id = ?', (user_id, analysis_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Ошибка удаления анализа {analysis_id}: {e}")
            return False
    
    # --- Методы для общих данных (generic_data, бывший field_data) ---
    def save_generic_data(self, key, value):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT OR REPLACE INTO generic_data (key, value) VALUES (?, ?)', (key, value))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка сохранения данных для ключа {key}: {e}")
            return False

    def get_generic_data(self, key):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT value FROM generic_data WHERE key = ?', (key,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Ошибка получения данных для ключа {key}: {e}")
            return None

    def delete_generic_data(self, key):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM generic_data WHERE key = ?', (key,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Ошибка удаления данных для ключа {key}: {e}")
            return False
            
    def generic_data_exists(self, key):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM generic_data WHERE key = ?', (key,))
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Ошибка при проверке ключа {key}: {e}")
            return False
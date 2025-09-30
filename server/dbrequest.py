import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

class requequest_to_first_db():
    def __init__(self):
        # Используем файл в текущей директории
        self.user_log = "db/user.db"
        # Создаем директорию если не существует
        os.makedirs(os.path.dirname(self.user_log), exist_ok=True)
        logger.info(f"Инициализация базы данных: {self.user_log}")
        self._create_table()

    def _create_table(self):
        """Создает таблицу пользователей, если она не существует"""
        try:
            with sqlite3.connect(self.user_log) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        login TEXT PRIMARY KEY,
                        password TEXT NOT NULL,
                        token TEXT UNIQUE
                    )
                ''')
                # Создаем индекс для быстрого поиска по токену
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_token ON users(token)
                ''')
                conn.commit()
                logger.info(f"База данных создана/проверена: {self.user_log}")
        except Exception as e:
            logger.error(f"Ошибка при создании базы данных: {e}")
            raise

    def get_token(self, login, password):
        """Получает токен пользователя по логину и паролю"""
        try:
            logger.info(f"Запрос токена для пользователя: {login}")
            with sqlite3.connect(self.user_log) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT token FROM users 
                    WHERE login = ? AND password = ?
                ''', (login, password))
                result = cursor.fetchone()
                if result:
                    logger.info(f"Токен найден для пользователя: {login}")
                    return result[0]
                else:
                    logger.warning(f"Токен не найден для пользователя: {login}")
                    return None
        except Exception as e:
            logger.error(f"Ошибка при получении токена для {login}: {e}")
            return None

    def add_new_user(self, login, password, token=None):
        """Добавляет нового пользователя"""
        try:
            logger.info(f"Добавление нового пользователя: {login}")
            with sqlite3.connect(self.user_log) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (login, password, token)
                    VALUES (?, ?, ?)
                ''', (login, password, token))
                conn.commit()
                logger.info(f"Пользователь {login} успешно добавлен")
                return True
        except sqlite3.IntegrityError as e:
            logger.warning(f"Пользователь {login} уже существует или токен не уникален: {e}")
            return False
        except Exception as e:
            logger.error(f"Ошибка при добавлении пользователя {login}: {e}")
            return False

    def user_exists(self, login):
        """Проверяет существование пользователя"""
        try:
            logger.debug(f"Проверка существования пользователя: {login}")
            with sqlite3.connect(self.user_log) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM users WHERE login = ?', (login,))
                exists = cursor.fetchone() is not None
                logger.debug(f"Пользователь {login} существует: {exists}")
                return exists
        except Exception as e:
            logger.error(f"Ошибка при проверке пользователя {login}: {e}")
            return False

    def if_token_exist(self, token):
        """Проверяет существование токена в базе данных"""
        try:
            logger.debug(f"Проверка существования токена: {token}")
            with sqlite3.connect(self.user_log) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM users WHERE token = ?', (token,))
                exists = cursor.fetchone() is not None
                logger.debug(f"Токен существует: {exists}")
                return exists
        except Exception as e:
            logger.error(f"Ошибка при проверке токена: {e}")
            return False
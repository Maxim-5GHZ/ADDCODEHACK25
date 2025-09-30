import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

class requequest_to_user_login():
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



"""класс для работы с данными пользователей"""


class request_to_user_data():
    def __init__(self):
        self.user_data = "db/user_data.db"
        os.makedirs(os.path.dirname(self.user_data), exist_ok=True)
        logger.info(f"Инициализация базы данных: {self.user_data}")
        self._create_table()

    def _create_table(self):
        """Создает таблицу пользовательских данных, если она не существует"""
        try:
            with sqlite3.connect(self.user_data) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_data (
                        token TEXT PRIMARY KEY,
                        key_array TEXT NOT NULL
                    )
                ''')
                # Создаем индекс для быстрого поиска по токену
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_data_token ON user_data(token)
                ''')
                conn.commit()
                logger.info(f"Таблица user_data создана/проверена: {self.user_data}")
        except Exception as e:
            logger.error(f"Ошибка при создании таблицы user_data: {e}")
            raise

    def save_user_data(self, token, key_array):
        """Сохраняет или обновляет данные пользователя по токену"""
        try:
            logger.info(f"Сохранение данных для токена: {token}")
            with sqlite3.connect(self.user_data) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO user_data (token, key_array)
                    VALUES (?, ?)
                ''', (token, key_array))
                conn.commit()
                logger.info(f"Данные для токена {token} успешно сохранены")
                return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных для токена {token}: {e}")
            return False

    def get_user_data(self, token):
        """Получает key_array по токену"""
        try:
            logger.info(f"Запрос данных для токена: {token}")
            with sqlite3.connect(self.user_data) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT key_array FROM user_data 
                    WHERE token = ?
                ''', (token,))
                result = cursor.fetchone()
                if result:
                    logger.info(f"Данные найдены для токена: {token}")
                    return result[0]
                else:
                    logger.warning(f"Данные не найдены для токена: {token}")
                    return None
        except Exception as e:
            logger.error(f"Ошибка при получении данных для токена {token}: {e}")
            return None

    def update_user_data(self, token, key_array):
        """Обновляет key_array для существующего токена"""
        try:
            logger.info(f"Обновление данных для токена: {token}")
            with sqlite3.connect(self.user_data) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE user_data 
                    SET key_array = ?
                    WHERE token = ?
                ''', (key_array, token))

                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Данные для токена {token} успешно обновлены")
                    return True
                else:
                    logger.warning(f"Токен {token} не найден для обновления")
                    return False
        except Exception as e:
            logger.error(f"Ошибка при обновлении данных для токена {token}: {e}")
            return False

    def edit_key_array(self, token, new_keys=None, keys_to_add=None, keys_to_remove=None):

        try:
            logger.info(f"Редактирование массива ключей для токена: {token}")

            with sqlite3.connect(self.user_data) as conn:
                cursor = conn.cursor()

                # Получаем текущий массив ключей
                cursor.execute('SELECT key_array FROM user_data WHERE token = ?', (token,))
                result = cursor.fetchone()

                if not result:
                    logger.warning(f"Токен {token} не найден для редактирования")
                    return False

                current_key_array = result[0]

                # Обрабатываем массив ключей в зависимости от переданных параметров
                if new_keys is not None:
                    # Полная замена массива
                    updated_key_array = new_keys
                else:
                    updated_key_array = current_key_array

                    # Добавляем ключи
                    if keys_to_add:
                        # Предполагаем, что ключи разделены запятыми или другим разделителем
                        current_keys = set(updated_key_array.split(',')) if updated_key_array else set()
                        keys_to_add_set = set(keys_to_add.split(','))
                        updated_keys = current_keys.union(keys_to_add_set)
                        updated_key_array = ','.join(updated_keys)

                    # Удаляем ключи
                    if keys_to_remove:
                        current_keys = set(updated_key_array.split(',')) if updated_key_array else set()
                        keys_to_remove_set = set(keys_to_remove.split(','))
                        updated_keys = current_keys - keys_to_remove_set
                        updated_key_array = ','.join(updated_keys) if updated_keys else ""

                # Обновляем запись в базе данных
                cursor.execute('''
                    UPDATE user_data 
                    SET key_array = ?
                    WHERE token = ?
                ''', (updated_key_array, token))

                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Массив ключей для токена {token} успешно отредактирован")
                    logger.debug(f"Новый массив ключей: {updated_key_array}")
                    return True
                else:
                    logger.warning(f"Не удалось обновить массив ключей для токена {token}")
                    return False

        except Exception as e:
            logger.error(f"Ошибка при редактировании массива ключей для токена {token}: {e}")
            return False

    def delete_user_data(self, token):
        """Удаляет данные пользователя по токену"""
        try:
            logger.info(f"Удаление данных для токена: {token}")
            with sqlite3.connect(self.user_data) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM user_data WHERE token = ?', (token,))

                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Данные для токена {token} успешно удалены")
                    return True
                else:
                    logger.warning(f"Токен {token} не найден для удаления")
                    return False
        except Exception as e:
            logger.error(f"Ошибка при удалении данных для токена {token}: {e}")
            return False

    def user_data_exists(self, token):
        """Проверяет существование данных для токена"""
        try:
            logger.debug(f"Проверка существования данных для токена: {token}")
            with sqlite3.connect(self.user_data) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM user_data WHERE token = ?', (token,))
                exists = cursor.fetchone() is not None
                logger.debug(f"Данные для токена {token} существуют: {exists}")
                return exists
        except Exception as e:
            logger.error(f"Ошибка при проверке данных для токена {token}: {e}")
            return False

    def get_all_tokens(self):
        """Получает список всех токенов в базе данных"""
        try:
            logger.debug("Получение списка всех токенов")
            with sqlite3.connect(self.user_data) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT token FROM user_data')
                tokens = [row[0] for row in cursor.fetchall()]
                logger.debug(f"Найдено токенов: {len(tokens)}")
                return tokens
        except Exception as e:
            logger.error(f"Ошибка при получении списка токенов: {e}")
            return []








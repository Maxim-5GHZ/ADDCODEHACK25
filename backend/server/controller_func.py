import random
import logging
from fastapi.responses import FileResponse
import time
import os

logger = logging.getLogger(__name__)

class controller_func():
    def __init__(self, user_bd, user_data, field_data):
        self.user_bd = user_bd
        self.user_data = user_data
        self.field_data = field_data

    async def reed__root(self):
        logger.info("Запрос главной страницы")
        try:
            return FileResponse("scrcontroller_func/index.html")
        except Exception as e:
            logger.error(f"Ошибка при загрузке index.html: {e}")
            return {"status": "error", "detail": "Файл не найден"}

    async def ico(self):
        logger.debug("Запрос favicon.ico")
        try:
            return FileResponse("scr/favicon.ico")
        except Exception as e:
            logger.warning(f"Favicon не найден: {e}")
            return {"status": "error", "detail": "Favicon не найден"}

    async def health_check(self):
        """Проверка здоровья сервера"""
        return {
            "status": "healthy",
            "message": "Server is running",
            "timestamp": time.time()
        }

    async def get_from_scr(self, file: str):
        logger.info(f"Запрос {file}")
        if os.path.exists(f"scr/{file}"):
            return FileResponse(f"scr/{file}")
        else:
            return {"status": "error", "detail": "Файл не найден"}

    async def save_data_by_token(self, token: str, key_array: str):
        """
        Сохраняет данные пользователя по токену
        """
        logger.info(f"Запрос на сохранение данных для токена: {token}")

        try:
            if not self.user_bd.if_token_exist(token):
                logger.warning(f"Попытка сохранения данных для несуществующего токена: {token}")
                return {
                    "status": "error",
                    "detail": "Токен не найден"
                }

            success = self.user_data.save_user_data(token, key_array)

            if not success:
                logger.error(f"Не удалось сохранить данные для токена: {token}")
                return {
                    "status": "error",
                    "detail": "Не удалось сохранить данные"
                }

            logger.info(f"Данные для токена {token} успешно сохранены")
            return {
                "status": "success",
                "message": "Данные успешно сохранены",
                "token": token
            }

        except Exception as e:
            logger.error(f"Ошибка при сохранении данных для токена {token}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}

    async def get_field_by_token(self, token: str):
        logger.info(f"Запрос данных для токена: {token}")
        try:
            if self.user_data.user_data_exists(token):
                keys = self.user_data.get_user_data(token)
                return {
                    "status": "success",
                    "keys": keys
                }
            else:
                return {
                    "status": "dismiss",
                    "message": "Данные не найдены"
                }
        except Exception as e:
            logger.error(f"Ошибка при получении данных для токена {token}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}

    async def get_log(self, password: str):
        logger.info("Запрос логов администратора")
        try:
            if password == "12345":
                return FileResponse("app.log")
            else:
                return {
                    "status": "error",
                    "detail": "Доступ запрещен"
                }
        except Exception as e:
            logger.error(f"Ошибка при чтении логов: {e}")
            return {"status": "error", "detail": "Файл логов не найден"}

    async def get_token(self, login: str, password: str):
        logger.info(f"Запрос токена для пользователя: {login}")
        try:
            token = self.user_bd.get_token(login, password)

            if token is None:
                if not self.user_bd.user_exists(login):
                    logger.warning(f"Пользователь не найден: {login}")
                    return {
                        "status": "error",
                        "detail": "Пользователь не найден"
                    }
                else:
                    logger.warning(f"Неверный пароль для пользователя: {login}")
                    return {
                        "status": "error",
                        "detail": "Неверный пароль"
                    }

            logger.info(f"Токен успешно выдан для пользователя: {login}")
            return {
                "status": "success",
                "token": token,
                "message": "Токен успешно получен"
            }
        except Exception as e:
            logger.error(f"Ошибка в get_token для {login}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}

    async def add_user(self, login: str, password: str):
        """
        Добавление нового пользователя
        """
        logger.info(f"Запрос на добавление пользователя: {login}")

        try:
            if self.user_bd.user_exists(login):
                logger.warning(f"Попытка регистрации существующего пользователя: {login}")
                return {
                    "status": "error",
                    "detail": "Пользователь с таким логином уже существует"
                }

            logger.info(f"Генерация токена для пользователя: {login}")
            token = str(random.randint(10 * 10 ** 20, 10 * 10 ** 21))
            while self.user_bd.if_token_exist(token):
                logger.debug(f"Токен {token} уже существует, генерируем новый")
                token = str(random.randint(10 * 10 ** 20, 10 * 10 ** 21))

            logger.info(f"Добавление пользователя {login} с токеном: {token}")
            success = self.user_bd.add_new_user(login, password, token)

            if not success:
                logger.error(f"Не удалось добавить пользователя: {login}")
                return {
                    "status": "error",
                    "detail": "Не удалось добавить пользователя"
                }

            logger.info(f"Пользователь {login} успешно зарегистрирован")
            return {
                "status": "success",
                "message": "Пользователь успешно добавлен",
                "login": login
            }
        except Exception as e:
            logger.error(f"Ошибка в add_user для {login}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}

    async def update_user_data(self, token: str, key_array: str):
        """Обновление данных пользователя по токену"""
        logger.info(f"Запрос на обновление данных для токена: {token}")
        try:
            success = self.user_data.update_user_data(token, key_array)

            if success:
                return {
                    "status": "success",
                    "message": "Данные успешно обновлены",
                    "token": token
                }
            else:
                return {
                    "status": "error",
                    "detail": "Токен не найден или данные не обновлены"
                }
        except Exception as e:
            logger.error(f"Ошибка при обновлении данных для токена {token}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}

    async def edit_user_data(self, token: str, new_keys: str = None, keys_to_add: str = None,
                             keys_to_remove: str = None):
        """Частичное редактирование массива ключей"""
        logger.info(f"Запрос на редактирование данных для токена: {token}")
        try:
            success = self.user_data.edit_key_array(
                token,
                new_keys,
                keys_to_add,
                keys_to_remove
            )

            if success:
                return {
                    "status": "success",
                    "message": "Данные успешно отредактированы",
                    "token": token
                }
            else:
                return {
                    "status": "error",
                    "detail": "Токен не найден или данные не отредактированы"
                }
        except Exception as e:
            logger.error(f"Ошибка при редактировании данных для токена {token}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}

    async def delete_user_data(self, token: str):
        """Удаление данных пользователя по токену"""
        logger.info(f"Запрос на удаление данных для токена: {token}")
        try:
            success = self.user_data.delete_user_data(token)

            if success:
                return {
                    "status": "success",
                    "message": "Данные успешно удалены",
                    "token": token
                }
            else:
                return {
                    "status": "error",
                    "detail": "Токен не найден или данные не удалены"
                }
        except Exception as e:
            logger.error(f"Ошибка при удалении данных для токена {token}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}

    async def check_user_data_exists(self, token: str):
        """Проверка существования данных пользователя"""
        logger.info(f"Запрос проверки данных для токена: {token}")
        try:
            exists = self.user_data.user_data_exists(token)

            return {
                "status": "success",
                "exists": exists,
                "token": token
            }
        except Exception as e:
            logger.error(f"Ошибка при проверке данных для токена {token}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}

    async def set_field_data(self, field: str, data: str, token: str):
        """
        Установка или обновление данных для поля
        """
        logger.info(f"Запрос на установку данных для поля: {field}")

        try:
            # Проверяем авторизацию пользователя
            if not self.user_bd.if_token_exist(token):
                logger.warning(f"Попытка установки данных с невалидным токеном: {token}")
                return {
                    "status": "error",
                    "detail": "Невалидный токен"
                }

            success = self.field_data.edit_field_data(field, data)

            if success:
                logger.info(f"Данные для поля {field} успешно установлены")
                return {
                    "status": "success",
                    "message": "Данные поля успешно сохранены",
                    "field": field
                }
            else:
                logger.error(f"Не удалось сохранить данные для поля: {field}")
                return {
                    "status": "error",
                    "detail": "Не удалось сохранить данные поля"
                }

        except Exception as e:
            logger.error(f"Ошибка при сохранении данных для поля {field}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}

    async def get_field_data(self, field: str, token: str = None):
        """
        Получение данных по названию поля
        """
        logger.info(f"Запрос данных для поля: {field}")

        try:
            # Опциональная проверка авторизации
            if token and not self.user_bd.if_token_exist(token):
                logger.warning(f"Попытка получения данных с невалидным токеном: {token}")
                return {
                    "status": "error",
                    "detail": "Невалидный токен"
                }

            data = self.field_data.get_field_data(field)

            if data is not None:
                logger.info(f"Данные для поля {field} успешно получены")
                return {
                    "status": "success",
                    "field": field,
                    "data": data
                }
            else:
                logger.warning(f"Данные для поля {field} не найдены")
                return {
                    "status": "dismiss",
                    "message": "Данные поля не найдены",
                    "field": field
                }

        except Exception as e:
            logger.error(f"Ошибка при получении данных для поля {field}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}

    async def delete_field_data(self, field: str, token: str):
        """
        Удаление данных поля
        """
        logger.info(f"Запрос на удаление данных поля: {field}")

        try:
            # Проверяем авторизацию пользователя
            if not self.user_bd.if_token_exist(token):
                logger.warning(f"Попытка удаления данных с невалидным токеном: {token}")
                return {
                    "status": "error",
                    "detail": "Невалидный токен"
                }

            success = self.field_data.delete_field_data(field)

            if success:
                logger.info(f"Данные поля {field} успешно удалены")
                return {
                    "status": "success",
                    "message": "Данные поля успешно удалены",
                    "field": field
                }
            else:
                logger.warning(f"Поле {field} не найдено для удаления")
                return {
                    "status": "error",
                    "detail": "Поле не найдено"
                }

        except Exception as e:
            logger.error(f"Ошибка при удалении данных поля {field}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}

    async def check_field_exists(self, field: str, token: str = None):
        logger.info(f"Запрос проверки существования поля: {field}")

        try:
            # Опциональная проверка авторизации
            if token and not self.user_bd.if_token_exist(token):
                logger.warning(f"Попытка проверки поля с невалидным токеном: {token}")
                return {
                    "status": "error",
                    "detail": "Невалидный токен"
                }

            exists = self.field_data.field_exists(field)

            return {
                "status": "success",
                "field": field,
                "exists": exists
            }

        except Exception as e:
            logger.error(f"Ошибка при проверке поля {field}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}

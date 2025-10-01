import uvicorn
import dbrequest
import random
import subprocess
import signal
import re
import logging
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import time
import os

logger = logging.getLogger(__name__)


class controller():
    def __init__(self,port):
        self._kill_process_on_port(port)
        logger.info("Инициализация контроллера...")
        self.app = FastAPI()
        self.user_bd = dbrequest.requequest_to_user_login()
        self.user_data = dbrequest.request_to_user_data()
        self.field_data = dbrequest.request_to_field_data()  # Добавляем экземпляр для работы с полями

        os.makedirs("html", exist_ok=True)
        os.makedirs("ico", exist_ok=True)

        self.app.mount("/static", StaticFiles(directory="."), name="static")
        logger.info("Контроллер инициализирован")

    def _kill_process_on_port(self,port):
        pid = None
        try:
            result = subprocess.run(
                ['lsof', '-ti', f'tcp:{port}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                pid = int(result.stdout.strip().split('\n')[0])
                print(f"Найден процесс с PID {pid} через lsof")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            pass
        if not pid:
            try:
                result = subprocess.run(
                    ['ss', '-tlnp'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    for line in result.stdout.splitlines():
                        if f':{port}' in line and 'LISTEN' in line:
                            match = re.search(r'pid=(\d+)', line)
                            if match:
                                pid = int(match.group(1))
                                print(f"Найден процесс с PID {pid} через ss")
                                break
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError, ValueError):
                pass

        if not pid:
            print(f"Не найден процесс, занимающий порт {port}.")
            return False
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"Отправлен SIGTERM процессу с PID {pid}.")

            time.sleep(2)

            try:
                os.kill(pid, 0)
                print(f"Процесс {pid} не ответил на SIGTERM, отправляем SIGKILL.")
                os.kill(pid, signal.SIGKILL)
                time.sleep(1)
            except OSError:
                pass

            print(f"Процесс с PID {pid} на порту {port} успешно завершен.")
            return True

        except ProcessLookupError:
            print(f"Процесс с PID {pid} уже завершен.")
            return True
        except PermissionError:
            print(f"Недостаточно прав для завершения процесса {pid}. Запустите с sudo.")
            return False
        except Exception as e:
            print(f"Ошибка при завершении процесса {pid}: {e}")
            return False


    def _controllers(self):
        logger.info("Регистрация маршрутов...")

        @self.app.get("/")
        async def read_root():
            logger.info("Запрос главной страницы")
            try:
                return FileResponse("scr/index.html")
            except Exception as e:
                logger.error(f"Ошибка при загрузке index.html: {e}")
                return {"status": "error", "detail": "Файл не найден"}

        @self.app.post("/savedata")
        async def save_data_by_token(
            token: str = Query(..., description="Токен пользователя"),
            key_array: str = Query(..., description="Массив ключей для сохранения")
        ):
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

        @self.app.get("/givefield")
        async def get_field_by_token(
            token: str = Query(..., description="Токен пользователя")
        ):
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

        @self.app.get("/log")
        async def get_log(
            password: str = Query(..., description="Пароль администратора")
        ):
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

        @self.app.get("/favicon.ico")
        async def ico():
            logger.debug("Запрос favicon.ico")
            try:
                return FileResponse("scr/favicon.ico")
            except Exception as e:
                logger.warning(f"Favicon не найден: {e}")
                return {"status": "error", "detail": "Favicon не найден"}

        @self.app.get("/get_token")
        async def get_token(
            login: str = Query(..., description="Логин пользователя"),
            password: str = Query(..., description="Пароль пользователя")
        ):
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

        @self.app.post("/add_user")
        async def add_user(
            login: str = Query(..., description="Логин пользователя"),
            password: str = Query(..., description="Пароль пользователя")
        ):
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

        @self.app.get("/health")
        async def health_check():
            """Проверка здоровья сервера"""
            return {
                "status": "healthy",
                "message": "Server is running",
                "timestamp": time.time()
            }

        @self.app.put("/data/update")
        async def update_user_data(
                token: str = Query(..., description="Токен пользователя"),
                key_array: str = Query(..., description="Новый массив ключей")
        ):
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

        @self.app.patch("/data/edit")
        async def edit_user_data(
                token: str = Query(..., description="Токен пользователя"),
                new_keys: str = Query(None, description="Полная замена массива ключей"),
                keys_to_add: str = Query(None, description="Ключи для добавления (через запятую)"),
                keys_to_remove: str = Query(None, description="Ключи для удаления (через запятую)")
        ):
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

        @self.app.delete("/data/delete")
        async def delete_user_data(
                token: str = Query(..., description="Токен пользователя")
        ):
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

        @self.app.get("/data/check")
        async def check_user_data_exists(
                token: str = Query(..., description="Токен пользователя")
        ):
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

        @self.app.post("/field/set")
        async def set_field_data(
                field: str = Query(..., description="Название поля"),
                data: str = Query(..., description="Данные для сохранения"),
                token: str = Query(..., description="Токен пользователя для авторизации")
        ):
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

        @self.app.get("/field/get")
        async def get_field_data(
                field: str = Query(..., description="Название поля"),
                token: str = Query(None, description="Токен пользователя (опционально)")
        ):
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

        @self.app.delete("/field/delete")
        async def delete_field_data(
                field: str = Query(..., description="Название поля для удаления"),
                token: str = Query(..., description="Токен пользователя для авторизации")
        ):
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

        @self.app.get("/field/check")
        async def check_field_exists(
                field: str = Query(..., description="Название поля для проверки"),
                token: str = Query(None, description="Токен пользователя (опционально)")
        ):
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

    def run(self):
        logger.info("Запуск сервера...")
        self._controllers()
        logger.info("Сервер запущен на 0.0.0.0:8000")
        uvicorn.run(
            self.app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True,
            timeout_keep_alive=5
        )
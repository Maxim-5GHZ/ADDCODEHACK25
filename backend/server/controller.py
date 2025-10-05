import uvicorn
from db import dbrequest
import subprocess
import controller_func
import signal
import re
import socket
import logging
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
import time
import os
import pathlib
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)



class controller():
    def __init__(self, port, use_https=True):
        logger.info("Инициализация контроллера...")
        self.use_https = use_https
        self.ssl_keyfile = None
        self.ssl_certfile = None

        protocol = "https" if self.use_https else "http"

        # Настройка путей для SSL сертификатов
        if self.use_https:
            self.ssl_keyfile = pathlib.Path("key.pem")
            self.ssl_certfile = pathlib.Path("cert.pem")
            # Проверка и генерация SSL сертификатов при необходимости
            self._setup_ssl()

        ip = self.get_local_ip()
        print(f"Сервер будет доступен по адресам ({protocol.upper()}):")
        print(f"Локально: {protocol}://localhost:8000")
        print(f"В сети: {protocol}://{ip}:8000")
        if not self.use_https:
            print("\nВНИМАНИЕ: Сервер запущен в небезопасном режиме HTTP.")
            print("Для производственного использования рекомендуется HTTPS.\n")
        print("Для остановки сервера нажмите Ctrl+C")

        self._kill_process_on_port(port)
        self.app = FastAPI()

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5137"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.user_bd = dbrequest.requequest_to_user_login()
        self.user_data = dbrequest.request_to_user_data()
        self.field_data = dbrequest.request_to_field_data()

        # Инициализируем controller_func с зависимостями
        self.func = controller_func.controller_func(self.user_bd, self.user_data, self.field_data)


        self.app.mount("/static", StaticFiles(directory="."), name="static")
        logger.info("Контроллер инициализирован")

    def _setup_ssl(self):
        """Проверяет наличие SSL-сертификатов и генерирует их, если они отсутствуют."""
        logger.info("Проверка SSL-сертификатов...")
        if self.ssl_keyfile.exists() and self.ssl_certfile.exists():
            logger.info("Найдены существующие SSL-сертификаты. Используются они.")
            print("Найдены существующие SSL-сертификаты (key.pem, cert.pem).")
            return

        logger.warning("SSL-сертификаты не найдены. Генерация самоподписанных сертификатов...")
        print("\nВНИМАНИЕ: SSL-сертификаты не найдены.")
        print("Генерируются самоподписанные сертификаты (key.pem, cert.pem).")
        print("Браузер будет выдавать предупреждение о безопасности, это нормально для самоподписанных сертификатов.")
        print("Для производственного использования замените эти файлы на сертификаты, выданные центром сертификации (CA).\n")

        try:
            # Команда для генерации сертификата с помощью OpenSSL
            command = [
                'openssl', 'req', '-x509',
                '-newkey', 'rsa:4096',
                '-keyout', str(self.ssl_keyfile),
                '-out', str(self.ssl_certfile),
                '-sha256',
                '-days', '365',
                '-nodes',  # Без пароля для ключа
                '-subj', '/CN=localhost' # Устанавливаем Common Name, чтобы избежать интерактивного ввода
            ]
            
            # Выполняем команду
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            logger.info("Самоподписанные SSL-сертификаты успешно сгенерированы.")
            print("Сертификаты успешно сгенерированы.")

        except FileNotFoundError:
            error_message = "КРИТИЧЕСКАЯ ОШИБКА: OpenSSL не найден. Невозможно сгенерировать SSL-сертификаты. Установите OpenSSL и попробуйте снова."
            logger.error(error_message)
            print(f"ОШИБКА: {error_message}")
            raise
        except subprocess.CalledProcessError as e:
            error_message = f"Ошибка при генерации сертификатов: {e.stderr}"
            logger.error(error_message)
            print(f"ОШИБКА: {error_message}")
            raise

    def get_local_ip(self):
        """Получает локальный IP-адрес компьютера"""
        try:
            logger.info("Получение локального IP-адреса...")
            # Создаем временное соединение чтобы определить IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(2)
            s.connect(("8.8.8.8", 80))  # Подключаемся к Google DNS
            local_ip = s.getsockname()[0]
            s.close()
            logger.info(f"Локальный IP-адрес: {local_ip}")
            return local_ip
        except Exception as e:
            logger.error(f"Ошибка при получении локального IP: {e}")
            # Пробуем альтернативный способ
            try:
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                logger.info(f"Локальный IP-адрес (альтернативный метод): {local_ip}")
                return local_ip
            except Exception as e2:
                logger.error(f"Альтернативный метод также не сработал: {e2}")
                return "127.0.0.1"

    def _kill_process_on_port(self, port):
        # ... (остается без изменений)
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

        @self.app.get("/scr/{file}")
        async def get_from_scr(file: str):
            return await self.func.get_from_scr(file)

        @self.app.get("/")
        async def read_root():
            return await self.func.reed__root()

        @self.app.post("/savedata")
        async def save_data_by_token(
                token: str = Query(..., description="Токен пользователя"),
                key_array: str = Query(..., description="Массив ключей для сохранения")
        ):
            return await self.func.save_data_by_token(token, key_array)

        @self.app.get("/givefield")
        async def get_field_by_token(
                token: str = Query(..., description="Токен пользователя")
        ):
            return await self.func.get_field_by_token(token)

        @self.app.get("/log")
        async def get_log(
                password: str = Query(..., description="Пароль администратора")
        ):
            return await self.func.get_log(password)

        @self.app.get("/favicon.ico")
        async def ico():
            return await self.func.ico()

        @self.app.get("/get_token")
        async def get_token(
                login: str = Query(..., description="Логин пользователя"),
                password: str = Query(..., description="Пароль пользователя")
        ):
            return await self.func.get_token(login, password)

        @self.app.post("/add_user")
        async def add_user(
                login: str = Query(..., description="Логин пользователя"),
                password: str = Query(..., description="Пароль пользователя")
        ):
            return await self.func.add_user(login, password)

        @self.app.get("/health")
        async def health_check():
            return await self.func.health_check()

        @self.app.put("/data/update")
        async def update_user_data(
                token: str = Query(..., description="Токен пользователя"),
                key_array: str = Query(..., description="Новый массив ключей")
        ):
            return await self.func.update_user_data(token, key_array)

        @self.app.patch("/data/edit")
        async def edit_user_data(
                token: str = Query(..., description="Токен пользователя"),
                new_keys: str = Query(None, description="Полная замена массива ключей"),
                keys_to_add: str = Query(None, description="Ключи для добавления (через запятую)"),
                keys_to_remove: str = Query(None, description="Ключи для удаления (через запятую)")
        ):
            return await self.func.edit_user_data(token, new_keys, keys_to_add, keys_to_remove)

        @self.app.delete("/data/delete")
        async def delete_user_data(
                token: str = Query(..., description="Токен пользователя")
        ):
            return await self.func.delete_user_data(token)

        @self.app.get("/data/check")
        async def check_user_data_exists(
                token: str = Query(..., description="Токен пользователя")
        ):
            return await self.func.check_user_data_exists(token)

        @self.app.post("/field/set")
        async def set_field_data(
                field: str = Query(..., description="Название поля"),
                data: str = Query(..., description="Данные для сохранения"),
                token: str = Query(..., description="Токен пользователя для авторизации")
        ):
            return await self.func.set_field_data(field, data, token)

        @self.app.get("/field/get")
        async def get_field_data(
                field: str = Query(..., description="Название поля"),
                token: str = Query(None, description="Токен пользователя (опционально)")
        ):
            return await self.func.get_field_data(field, token)

        @self.app.delete("/field/delete")
        async def delete_field_data(
                field: str = Query(..., description="Название поля для удаления"),
                token: str = Query(..., description="Токен пользователя для авторизации")
        ):
            return await self.func.delete_field_data(field, token)

        @self.app.get("/field/check")
        async def check_field_exists(
                field: str = Query(..., description="Название поля для проверки"),
                token: str = Query(None, description="Токен пользователя (опционально)")
        ):
            return await self.func.check_field_exists(field, token)

        @self.app.get("/image/rgb")
        async def get_rgb_image(
                lon: float = Query(..., description="Долгота"),
                lat: float = Query(..., description="Широта"),
                start_date: str = Query(..., description="Начальная дата (YYYY-MM-DD)"),
                end_date: str = Query(..., description="Конечная дата (YYYY-MM-DD)"),
                token: str = Query(..., description="Токен пользователя")
        ):
            return await self.func.get_rgb_image(lon, lat, start_date, end_date, token)

        @self.app.get("/image/red-channel")
        async def get_red_channel_image(
                lon: float = Query(..., description="Долгота"),
                lat: float = Query(..., description="Широта"),
                start_date: str = Query(..., description="Начальная дата (YYYY-MM-DD)"),
                end_date: str = Query(..., description="Конечная дата (YYYY-MM-DD)"),
                token: str = Query(..., description="Токен пользователя")
        ):
            return await self.func.get_red_channel_image(lon, lat, start_date, end_date, token)

        @self.app.get("/image/ndvi")
        async def get_ndvi_image(
                lon: float = Query(..., description="Долгота"),
                lat: float = Query(..., description="Широта"),
                start_date: str = Query(..., description="Начальная дата (YYYY-MM-DD)"),
                end_date: str = Query(..., description="Конечная дата (YYYY-MM-DD)"),
                token: str = Query(..., description="Токен пользователя")
        ):
            return await self.func.get_ndvi_image(lon, lat, start_date, end_date, token)
        
        @self.app.post("/analysis/perform")
        async def perform_analysis(
                token: str = Query(..., description="Токен пользователя"),
                lon: float = Query(..., description="Долгота"),
                lat: float = Query(..., description="Широта"),
                start_date: str = Query(..., description="Начальная дата (YYYY-MM-DD)"),
                end_date: str = Query(..., description="Конечная дата (YYYY-MM-DD)")
        ):
            return await self.func.perform_analysis(token, lon, lat, start_date, end_date)

        @self.app.get("/analysis/list")
        async def get_analyses_list(
                token: str = Query(..., description="Токен пользователя")
        ):
            return await self.func.get_analyses_list(token)

        @self.app.get("/analysis/{analysis_id}")
        async def get_analysis(
                analysis_id: str,
                token: str = Query(..., description="Токен пользователя")
        ):
            return await self.func.get_analysis(token, analysis_id)

        @self.app.delete("/analysis/{analysis_id}")
        async def delete_analysis(
                analysis_id: str,
                token: str = Query(..., description="Токен пользователя")
        ):
            return await self.func.delete_analysis(token, analysis_id)
        
        
    
    def run(self):
        protocol = "HTTPS" if self.use_https else "HTTP"
        logger.info(f"Запуск {protocol} сервера...")
        self._controllers()
        logger.info(f"Сервер запущен на 0.0.0.0:8000 с использованием {protocol}")
        
        uvicorn_config = {
            "host": "0.0.0.0",
            "port": 8000,
            "log_level": "info",
            "access_log": True,
            "timeout_keep_alive": 5,
        }

        if self.use_https:
            if not self.ssl_keyfile or not self.ssl_certfile:
                 logger.error("SSL файлы не были установлены для HTTPS режима.")
                 return
            uvicorn_config["ssl_keyfile"] = str(self.ssl_keyfile)
            uvicorn_config["ssl_certfile"] = str(self.ssl_certfile)
        
        uvicorn.run(self.app, **uvicorn_config)



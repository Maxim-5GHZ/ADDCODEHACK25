# --- START OF FILE controller.py ---

# --- START OF FILE controller.py ---

import uvicorn
from dbrequest import DatabaseManager # ИЗМЕНЕНО: импортируем новый класс
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
    def __init__(self, port, use_https=True,token_use=True):
        logger.info("Инициализация контроллера...")
        self.use_https = use_https
        self.token_use = token_use
        self.ssl_keyfile = None
        self.ssl_certfile = None

        protocol = "https" if self.use_https else "http"

        if self.use_https:
            self.ssl_keyfile = pathlib.Path("key.pem")
            self.ssl_certfile = pathlib.Path("cert.pem")
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
            allow_origins=["*"], # Можно заменить на адрес вашего фронтенда
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        # --- ИЗМЕНЕНО: Создаем один менеджер БД ---
        self.db = DatabaseManager() 
        self.func = controller_func.controller_func(self.db)
        # --- КОНЕЦ ИЗМЕНЕНИЙ ---

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
        
        try:
            command = [
                'openssl', 'req', '-x509', '-newkey', 'rsa:4096', '-keyout', str(self.ssl_keyfile),
                '-out', str(self.ssl_certfile), '-sha256', '-days', '365', '-nodes', 
                '-subj', '/CN=localhost'
            ]
            subprocess.run(command, check=True, capture_output=True, text=True)
            logger.info("Самоподписанные SSL-сертификаты успешно сгенерированы.")
            print("Сертификаты успешно сгенерированы.")
        except FileNotFoundError:
            error_message = "КРИТИЧЕСКАЯ ОШИБКА: OpenSSL не найден."
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
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.1)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"

    def _kill_process_on_port(self, port):
        pid = None
        try:
            result = subprocess.run(['lsof', '-ti', f'tcp:{port}'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                pid = int(result.stdout.strip().split('\n')[0])
        except (subprocess.CalledProcessError, FileNotFoundError, ValueError): pass
        
        if not pid: return False
        
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(2)
            try:
                os.kill(pid, 0)
                os.kill(pid, signal.SIGKILL)
            except OSError: pass
            print(f"Процесс с PID {pid} на порту {port} успешно завершен.")
            return True
        except (ProcessLookupError, PermissionError) as e:
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
        async def save_data_by_token(token: str = Query(...), key_array: str = Query(...)):
            return await self.func.save_data_by_token(token, key_array)

        @self.app.get("/givefield")
        async def get_field_by_token(token: str = Query(...)):
            return await self.func.get_field_by_token(token)

        @self.app.get("/log")
        async def get_log(password: str = Query(...)):
            return await self.func.get_log(password)

        @self.app.get("/favicon.ico")
        async def ico():
            return await self.func.ico()

        @self.app.get("/get_token")
        async def get_token(login: str = Query(...), password: str = Query(...)):
            return await self.func.get_token(login, password)

        @self.app.post("/add_user")
        async def add_user(login: str = Query(...), password: str = Query(...), first_name: str = Query(...), last_name: str = Query(...)):
            return await self.func.add_user(login, password, first_name, last_name)

        @self.app.get("/users/all")
        async def get_all_users(password: str = Query(...)):
            return await self.func.get_all_users(password)
            
        @self.app.get("/users/profile")
        async def get_user_profile(token: str = Query(...)):
            return await self.func.get_user_profile(token)

        @self.app.get("/health")
        async def health_check():
            return await self.func.health_check()

        # ... (маршруты для /data/..., /field/... остаются без изменений)
        @self.app.put("/data/update")
        async def update_user_data(token: str = Query(...), key_array: str = Query(...)):
            return await self.func.update_user_data(token, key_array)

        @self.app.patch("/data/edit")
        async def edit_user_data(token: str = Query(...), new_keys: str = Query(None), keys_to_add: str = Query(None), keys_to_remove: str = Query(None)):
            return await self.func.edit_user_data(token, new_keys, keys_to_add, keys_to_remove)

        @self.app.delete("/data/delete")
        async def delete_user_data(token: str = Query(...)):
            return await self.func.delete_user_data(token)

        @self.app.get("/data/check")
        async def check_user_data_exists(token: str = Query(...)):
            return await self.func.check_user_data_exists(token)

        @self.app.post("/field/set")
        async def set_field_data(field: str = Query(...), data: str = Query(...), token: str = Query(...)):
            return await self.func.set_field_data(field, data, token)

        @self.app.get("/field/get")
        async def get_field_data(field: str = Query(...), token: str = Query(None)):
            return await self.func.get_field_data(field, token)

        @self.app.delete("/field/delete")
        async def delete_field_data(field: str = Query(...), token: str = Query(...)):
            return await self.func.delete_field_data(field, token)

        @self.app.get("/field/check")
        async def check_field_exists(field: str = Query(...), token: str = Query(None)):
            return await self.func.check_field_exists(field, token)

        @self.app.get("/image/rgb")
        async def get_rgb_image(lon: float = Query(...), lat: float = Query(...), start_date: str = Query(...), end_date: str = Query(...), token: str = Query(...)):
            return await self.func.get_rgb_image(lon, lat, start_date, end_date, token)

        @self.app.get("/image/red-channel")
        async def get_red_channel_image(lon: float = Query(...), lat: float = Query(...), start_date: str = Query(...), end_date: str = Query(...), token: str = Query(...)):
            return await self.func.get_red_channel_image(lon, lat, start_date, end_date, token)

        @self.app.get("/image/ndvi")
        async def get_ndvi_image(lon: float = Query(...), lat: float = Query(...), start_date: str = Query(...), end_date: str = Query(...), token: str = Query(...)):
            return await self.func.get_ndvi_image(lon, lat, start_date, end_date, token)
        
        @self.app.post("/analysis/perform")
        async def perform_analysis(token: str = Query(...), start_date: str = Query(...), end_date: str = Query(...), lon: float = Query(None), lat: float = Query(None), radius_km: float = Query(0.5), polygon_coords: str = Query(None)):
            return await self.func.perform_analysis(token, start_date, end_date, lon, lat, radius_km, polygon_coords)

        @self.app.get("/analysis/list")
        async def get_analyses_list(token: str = Query(...)):
            return await self.func.get_analyses_list(token)

        @self.app.get("/analysis/{analysis_id}")
        async def get_analysis(analysis_id: str, token: str = Query(...)):
            return await self.func.get_analysis(token, analysis_id)

        @self.app.delete("/analysis/{analysis_id}")
        async def delete_analysis(analysis_id: str, token: str = Query(...)):
            return await self.func.delete_analysis(token, analysis_id)
        
        # <<< --- НАЧАЛО НОВОГО МАРШРУТА --- >>>
        @self.app.get("/analysis/{analysis_id}/recommendations")
        async def get_ai_recommendations(analysis_id: str, token: str = Query(...)):
            return await self.func.get_ai_recommendations(token, analysis_id,if_use_token=self.token_use)
        # <<< --- КОНЕЦ НОВОГО МАРШРУТА --- >>>
        
        # --- НОВЫЙ МАРШРУТ ---
        @self.app.get("/analysis/timeseries")
        async def get_historical_ndvi(
                token: str = Query(..., description="Токен пользователя"),
                lon: float = Query(None, description="Долгота центральной точки"),
                lat: float = Query(None, description="Широта центральной точки"),
                radius_km: float = Query(0.5, description="Радиус в километрах"),
                polygon_coords: str = Query(None, description="Координаты полигона в виде JSON-строки")
        ):
            return await self.func.get_historical_ndvi_data(token, lon, lat, radius_km, polygon_coords)
        
        # --- НОВЫЕ МАРШРУТЫ ДЛЯ УПРАВЛЕНИЯ ПОЛЯМИ ---
        @self.app.post("/fields/save")
        async def save_user_field(token: str = Query(...), field_name: str = Query(...), area_of_interest: str = Query(...)):
            return await self.func.save_user_field(token, field_name, area_of_interest)

        @self.app.get("/fields/list")
        async def get_user_fields(token: str = Query(...)):
            return await self.func.get_user_fields(token)

        @self.app.delete("/fields/{field_id}")
        async def delete_user_field(field_id: str, token: str = Query(...)):
            return await self.func.delete_user_field(token, field_id)


    def run(self):
        protocol = "HTTPS" if self.use_https else "HTTP"
        logger.info(f"Запуск {protocol} сервера...")
        self._controllers()
        logger.info(f"Сервер запущен на 0.0.0.0:8000 с использованием {protocol}")
        
        uvicorn_config = {
            "host": "0.0.0.0",
            "port": 8000,
            "log_level": "info",
        }

        if self.use_https:
            if not self.ssl_keyfile or not self.ssl_certfile:
                 logger.error("SSL файлы не были установлены для HTTPS режима.")
                 return
            uvicorn_config["ssl_keyfile"] = str(self.ssl_keyfile)
            uvicorn_config["ssl_certfile"] = str(self.ssl_certfile)
        
        uvicorn.run(self.app, **uvicorn_config)
import uvicorn
import dbrequest
import random
import logging
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

logger = logging.getLogger(__name__)


class controller():
    def __init__(self):
        logger.info("Инициализация контроллера...")
        self.app = FastAPI()
        self.user_bd = dbrequest.requequest_to_first_db()

        os.makedirs("html", exist_ok=True)
        os.makedirs("ico", exist_ok=True)

        self.app.mount("/static", StaticFiles(directory="."), name="static")
        logger.info("Контроллер инициализирован")

    def _controllers(self):
        logger.info("Регистрация маршрутов...")

        @self.app.get("/")
        async def read_root():
            logger.info("Запрос главной страницы")
            try:
                return FileResponse("html/index.html")
            except Exception as e:
                logger.error(f"Ошибка при загрузке index.html: {e}")
                return {"error": "Файл не найден", "detail": str(e)}

        @self.app.get("/log{password}")
        async def get_log(password : str):
            if password == "12345": return FileResponse("app.log")
            else:return "idi na xuy"

        @self.app.get("/favicon.ico")
        async def ico():
            logger.debug("Запрос favicon.ico")
            try:
                return FileResponse("ico/favicon.ico")
            except Exception as e:
                logger.warning(f"Favicon не найден: {e}")
                return {"error": "Favicon не найден"}

        @self.app.get("/get_token")
        async def get_token(login: str = Query(..., description="Логин пользователя"),
                            password: str = Query(..., description="Пароль пользователя")):
            """
            Получение токена пользователя по логину и паролю
            """
            logger.info(f"Запрос токена для пользователя: {login}")
            try:
                token = self.user_bd.get_token(login, password)

                if token is None:
                    # Проверяем, существует ли пользователь
                    if not self.user_bd.user_exists(login):
                        logger.warning(f"Пользователь не найден: {login}")
                        raise HTTPException(
                            status_code=404,
                            detail="Пользователь не найден"
                        )
                    else:
                        logger.warning(f"Неверный пароль для пользователя: {login}")
                        raise HTTPException(
                            status_code=401,
                            detail="Неверный пароль"
                        )

                logger.info(f"Токен успешно выдан для пользователя: {login}")
                return {
                    "status": "success",
                    "token": token
                }
            except Exception as e:
                logger.error(f"Ошибка в get_token для {login}: {e}")
                raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

        @self.app.post("/add_user")
        async def add_user(login: str = Query(..., description="Логин пользователя"),
                           password: str = Query(..., description="Пароль пользователя")):
            """
            Добавление нового пользователя
            """
            logger.info(f"Запрос на добавление пользователя: {login}")

            try:
                # Проверяем, не существует ли уже пользователь с таким логином
                if self.user_bd.user_exists(login):
                    logger.warning(f"Попытка регистрации существующего пользователя: {login}")
                    raise HTTPException(
                        status_code=409,
                        detail="Пользователь с таким логином уже существует"
                    )

                logger.info(f"Генерация токена для пользователя: {login}")
                token = str(random.randint(10 * 10 ** 20, 10 * 10 ** 21))
                while self.user_bd.if_token_exist(token):
                    logger.debug(f"Токен {token} уже существует, генерируем новый")
                    token = str(random.randint(10 * 10 ** 20, 10 * 10 ** 21))

                logger.info(f"Добавление пользователя {login} с токеном: {token}")
                success = self.user_bd.add_new_user(login, password, token)

                if not success:
                    logger.error(f"Не удалось добавить пользователя: {login}")
                    raise HTTPException(
                        status_code=500,
                        detail="Не удалось добавить пользователя"
                    )

                logger.info(f"Пользователь {login} успешно зарегистрирован")
                return {
                    "status": "success",
                    "message": "Пользователь успешно добавлен",
                    "login": login
                }
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Ошибка в add_user для {login}: {e}")
                raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

        @self.app.get("/health")
        async def health_check():
            """Проверка здоровья сервера"""
            return {"status": "healthy", "message": "Server is running"}

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
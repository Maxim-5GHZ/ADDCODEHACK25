# login.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QLabel, QLineEdit, QMessageBox, QPushButton)
from PySide6.QtCore import Qt, QThread, Signal
import aiohttp
import asyncio
import json
import ssl

class LoginWorker(QThread):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, base_url, is_login, username, password):
        super().__init__()
        self.base_url = base_url
        self.is_login = is_login
        self.username = username
        self.password = password

    async def check_server_availability(self):
        """Асинхронная проверка доступности сервера"""
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                async with session.get(f"{self.base_url}/health") as response:
                    return response.status == 200
        except Exception as e:
            print(f"Ошибка проверки сервера: {e}")
            return False

    async def make_server_request(self, endpoint, method="GET", params=None):
        """Асинхронный запрос к серверу"""
        try:
            url = f"{self.base_url}{endpoint}"
            timeout = aiohttp.ClientTimeout(total=10)
            connector = aiohttp.TCPConnector(ssl=False)

            async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                if method.upper() == "GET":
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            return await response.json()
                elif method.upper() == "POST":
                    async with session.post(url, params=params) as response:
                        if response.status == 200:
                            return await response.json()
                return None
        except Exception as e:
            print(f"Request error for {url}: {e}")
            return None

    async def perform_login(self):
        """Выполняет асинхронный вход или регистрацию"""
        try:
            # Проверяем доступность сервера
            if not await self.check_server_availability():
                return {"status": "server_unavailable"}

            if self.is_login:
                # Запрос на вход
                response = await self.make_server_request(
                    "/get_token",
                    method="GET",
                    params={"login": self.username, "password": self.password}
                )

                if response and response.get("status") == "success":
                    return {"status": "success", "token": response.get("token")}
                else:
                    error_msg = response.get("detail", "Ошибка входа") if response else "Ошибка соединения с сервером"
                    return {"status": "error", "message": error_msg}
            else:
                # Запрос на регистрацию
                response = await self.make_server_request(
                    "/add_user",
                    method="POST",
                    params={"login": self.username, "password": self.password}
                )

                if response and response.get("status") == "success":
                    # После успешной регистрации автоматически выполняем вход
                    login_response = await self.make_server_request(
                        "/get_token",
                        method="GET",
                        params={"login": self.username, "password": self.password}
                    )

                    if login_response and login_response.get("status") == "success":
                        return {"status": "success", "token": login_response.get("token")}
                    else:
                        return {"status": "success", "message": "Регистрация успешна! Теперь выполните вход."}
                else:
                    error_msg = response.get("detail", "Ошибка регистрации") if response else "Ошибка соединения с сервером"
                    return {"status": "error", "message": error_msg}

        except Exception as e:
            return {"status": "error", "message": f"Произошла ошибка: {str(e)}"}

    def run(self):
        """Запускает асинхронную операцию"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.perform_login())
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            loop.close()

class LoginDialog(QDialog):
    def __init__(self, is_login=True, parent=None):
        super().__init__(parent)
        self.is_login = is_login
        self.token = None
        self.base_url = "https://localhost:8000"
        self.worker = None
        self.setup_ui()
        self.apply_styles()

    def apply_styles(self):
        """Применяет CSS стили для диалога входа"""
        style = """
        QDialog {
            background-color: #F5F5F5;
            border-radius: 15px;
        }
        QLabel {
            font-weight: bold;
            color: #333333;
        }
        QLineEdit {
            border: 2px solid #CCCCCC;
            border-radius: 10px;
            padding: 8px;
            font-size: 14px;
            background-color: white;
            min-height: 20px;
        }
        QLineEdit:focus {
            border: 2px solid #32CD32;
        }
        QPushButton {
            border: 2px solid #2E8B57;
            border-radius: 15px;
            padding: 12px 20px;
            font-weight: bold;
            font-size: 14px;
            background-color: #F8F8F8;
            color: #2E8B57;
            min-height: 25px;
        }
        QPushButton:hover {
            background-color: #E8E8E8;
            border: 2px solid #228B22;
        }
        QPushButton:pressed {
            background-color: #D8D8D8;
            border: 2px solid #006400;
        }
        QPushButton#login_push_button {
            background-color: #32CD32;
            color: white;
            border: 2px solid #228B22;
        }
        QPushButton#login_push_button:hover {
            background-color: #28A428;
            border: 2px solid #1E7A1E;
        }
        QPushButton:disabled {
            background-color: #CCCCCC;
            color: #666666;
            border: 2px solid #999999;
        }
        """
        self.setStyleSheet(style)

    def setup_ui(self):
        self.setWindowTitle("Вход" if self.is_login else "Регистрация")
        self.resize(400, 350)
        self.setModal(True)

        # Главный layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)

        # Заголовок
        title_label = QLabel("Вход в систему" if self.is_login else "Регистрация")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            margin: 10px;
            color: #2E8B57;
            padding: 5px;
        """)
        main_layout.addWidget(title_label)

        main_layout.addStretch(1)

        # Поле логина
        username_label = QLabel("Логин:")
        username_label.setStyleSheet("margin-bottom: 5px;")
        main_layout.addWidget(username_label)

        self.username_line_edit = QLineEdit()
        self.username_line_edit.setPlaceholderText("Введите логин")
        main_layout.addWidget(self.username_line_edit)

        # Поле пароля
        password_label = QLabel("Пароль:")
        password_label.setStyleSheet("margin-top: 15px; margin-bottom: 5px;")
        main_layout.addWidget(password_label)

        self.password_line_edit = QLineEdit()
        self.password_line_edit.setPlaceholderText("Введите пароль")
        self.password_line_edit.setEchoMode(QLineEdit.Password)
        main_layout.addWidget(self.password_line_edit)

        # Индикатор загрузки
        self.loading_label = QLabel("Выполняется вход...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("color: #2E8B57; font-weight: bold;")
        self.loading_label.hide()
        main_layout.addWidget(self.loading_label)

        main_layout.addStretch(2)

        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.login_push_button = QPushButton("Войти" if self.is_login else "Зарегистрироваться")
        self.login_push_button.setObjectName("login_push_button")
        self.login_push_button.clicked.connect(self.handle_login)
        buttons_layout.addWidget(self.login_push_button)

        cancel_push_button = QPushButton("Отмена")
        cancel_push_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_push_button)

        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

    def set_loading(self, loading):
        """Устанавливает состояние загрузки"""
        self.login_push_button.setEnabled(not loading)
        cancel_push_button = self.findChild(QPushButton, "Отмена")
        if cancel_push_button:
            cancel_push_button.setEnabled(not loading)

        if loading:
            self.loading_label.show()
        else:
            self.loading_label.hide()

    def handle_login(self):
        username = self.username_line_edit.text()
        password = self.password_line_edit.text()

        if not username or not password:
            self.show_custom_message("Ошибка", "Заполните все поля!")
            return

        # Запускаем асинхронный worker
        self.set_loading(True)
        self.worker = LoginWorker(self.base_url, self.is_login, username, password)
        self.worker.finished.connect(self.on_login_finished)
        self.worker.error.connect(self.on_login_error)
        self.worker.start()

    def on_login_finished(self, result):
        """Обрабатывает завершение асинхронного входа"""
        self.set_loading(False)

        if result["status"] == "server_unavailable":
            self.show_custom_message(
                "Сервер недоступен",
                "Сервер не отвечает.\n\n"
                "Убедитесь, что сервер запущен на https://localhost:8000\n"
                "Если сервер использует самоподписанные SSL сертификаты, "
                "это нормально - просто продолжайте."
            )
            # В демо-режиме разрешаем вход без сервера
            self.token = f"demo_token_{self.username_line_edit.text()}"
            self.accept()
        elif result["status"] == "success":
            if "token" in result:
                self.token = result["token"]
                self.accept()
            else:
                self.show_custom_message("Успех", result.get("message", "Операция выполнена успешно"))
        else:
            self.show_custom_message("Ошибка", result.get("message", "Неизвестная ошибка"))

    def on_login_error(self, error_message):
        """Обрабатывает ошибку асинхронного входа"""
        self.set_loading(False)
        self.show_custom_message("Ошибка", f"Произошла ошибка: {error_message}")

    def get_token(self):
        """Возвращает полученный токен"""
        return self.token

    def show_custom_message(self, title, text):
        """Показывает кастомное сообщение"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.NoIcon)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
                min-width: 400px;
                min-height: 200px;
                color: black;
            }
            QMessageBox QLabel {
                color: black;
                font-size: 11px;
                min-width: 400px;
                min-height: 150px;
                qproperty-alignment: AlignCenter;
            }
            QMessageBox QPushButton {
                font-size: 11px;
                min-width: 80px;
                min-height: 30px;
                padding: 6px;
                color: black;
                background-color: #f0f0f0;
            }
            QMessageBox QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        msg.exec()

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QLabel, QLineEdit, QMessageBox, QPushButton)
from PySide6.QtCore import Qt

class LoginDialog(QDialog):
    def __init__(self, is_login=True, parent=None):
        super().__init__(parent)
        self.is_login = is_login
        self.setup_ui()
        self.apply_styles()

    def apply_styles(self):
        """Применяет CSS стили для диалога входа"""
        style = """
        QDialog {
            background-color: #F5F5F5;
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
        """
        self.setStyleSheet(style)

    def setup_ui(self):
        self.setWindowTitle("Вход" if self.is_login else "Регистрация")
        self.setFixedSize(350, 250)
        self.setModal(True)

        layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel("Вход в систему" if self.is_login else "Регистрация")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 15px; color: #2E8B57;")
        layout.addWidget(title_label)

        # Поле логина
        username_label = QLabel("Логин:")
        layout.addWidget(username_label)

        self.username_line_edit = QLineEdit()
        self.username_line_edit.setPlaceholderText("Введите логин")
        layout.addWidget(self.username_line_edit)

        # Поле пароля
        password_label = QLabel("Пароль:")
        layout.addWidget(password_label)

        self.password_line_edit = QLineEdit()
        self.password_line_edit.setPlaceholderText("Введите пароль")
        self.password_line_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_line_edit)

        # Кнопки
        buttons_layout = QHBoxLayout()

        self.login_push_button = QPushButton("Войти" if self.is_login else "Зарегистрироваться")
        self.login_push_button.setObjectName("login_push_button")
        self.login_push_button.clicked.connect(self.handle_login)
        buttons_layout.addWidget(self.login_push_button)

        cancel_push_button = QPushButton("Отмена")
        cancel_push_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_push_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def handle_login(self):
        username = self.username_line_edit.text()
        password = self.password_line_edit.text()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        # Здесь можно добавить логику проверки логина/пароля
        QMessageBox.information(self, "Успех",
                               f"Данные приняты!\nЛогин: {username}\nПароль: {password}")
        self.accept()

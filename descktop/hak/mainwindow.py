# This Python file uses the following encoding: utf-8
import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtCore import Qt

from ui_form import Ui_MainWindow
from login import LoginDialog
from map import MapDialog
from bridge.map_bridge import MapBridge

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Применяем стили
        self.apply_styles()

        # Подключаем обработчики событий для кнопок
        self.setup_ui_connections()

    def apply_styles(self):
        """Применяет CSS стили для красивого интерфейса"""
        style = """
        /* Стиль для всех кнопок */
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

        /* Специальный стиль для кнопки анализа поля */
        QPushButton#pushButton_Anayze_field {
            background-color: #32CD32;
            color: white;
            border: 2px solid #228B22;
            font-size: 16px;
            font-weight: bold;
            padding: 15px 25px;
            border-radius: 20px;
        }

        QPushButton#pushButton_Anayze_field:hover {
            background-color: #28A428;
            border: 2px solid #1E7A1E;
        }

        QPushButton#pushButton_Anayze_field:pressed {
            background-color: #1E7A1E;
            border: 2px solid #145214;
        }

        /* Стиль для метки с координатами */
        QLabel#label_analyze {
            border: 2px solid #32CD32;
            border-radius: 10px;
            padding: 10px;
            background-color: #F0FFF0;
            color: #006400;
            font-weight: bold;
            font-size: 14px;
        }

        /* Стиль для главного окна */
        MainWindow {
            background-color: #F5F5F5;
        }
        """
        self.setStyleSheet(style)

    def handle_map_click(self, lat, lng):
        """Обрабатывает клик по карте - получает координаты"""
        try:
            coordinates_text = f"Широта: {lat:.6f}, Долгота: {lng:.6f}"

            # Выводим координаты в label_analyze
            if hasattr(self.ui, 'label_analyze'):
                self.ui.label_analyze.setText(coordinates_text)
                self.ui.label_analyze.setStyleSheet("color: green; font-weight: bold; padding: 10px; border: 2px solid #32CD32; border-radius: 10px; background-color: #F0FFF0;")
                print("Координаты установлены в label_analyze")
            else:
                print("label_analyze не найден в UI")

            # Принудительно обновляем интерфейс
            QApplication.processEvents()

        except Exception as e:
            print(f"Ошибка в handle_map_click: {e}")

    def setup_ui_connections(self):
        # Подключение кнопок входа и регистрации
        if hasattr(self.ui, 'login_main_button'):
            self.ui.login_main_button.clicked.connect(self.show_login_dialog)

        if hasattr(self.ui, 'register_main_button'):
            self.ui.register_main_button.clicked.connect(self.show_register_dialog)

        # Подключение кнопки анализа поля - теперь она открывает карту
        if hasattr(self.ui, 'pushButton_Anayze_field'):
            self.ui.pushButton_Anayze_field.clicked.connect(self.open_map_for_analysis)

    def open_map_for_analysis(self):
        """Открывает карту для выбора точки"""
        # Создаем диалог с картой
        map_dialog = MapDialog(self, coord_callback=self.handle_map_click)
        map_dialog.exec()

    def show_login_dialog(self):
        dialog = LoginDialog(is_login=True, parent=self)
        dialog.exec()

    def show_register_dialog(self):
        dialog = LoginDialog(is_login=False, parent=self)
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.showMaximized()
    sys.exit(app.exec())

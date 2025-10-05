# mainwindow.py
import sys
import os
import json
import requests
import urllib3
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QApplication, QMainWindow, QMessageBox, QLabel,
                               QWidget, QDialog, QProgressDialog)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QPixmap, QPainter, QColor, QIcon, QFont

from ui_form import Ui_MainWindow
from login import LoginDialog
from map import MapDialog
from bridge.map_bridge import MapBridge

# Отключаем предупреждения о SSL для самоподписанных сертификатов
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Асинхронные рабочие потоки
class AnalysisWorker(QThread):
    """Поток для выполнения анализа поля"""
    finished = Signal(object)
    error = Signal(str)
    progress = Signal(str)

    def __init__(self, make_request_func, field_name, lat, lng, token):
        super().__init__()
        self.make_request_func = make_request_func
        self.field_name = field_name
        self.lat = lat
        self.lng = lng
        self.token = token

    def run(self):
        try:
            self.progress.emit(f"Начинаем анализ поля {self.field_name}...")

            # Формируем даты для анализа (последние 30 дней)
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

            self.progress.emit("Отправляем запрос на сервер...")

            # Выполняем запрос
            response = self.make_request_func(
                "/analysis/perform",
                method="POST",
                params={
                    "lon": self.lng,
                    "lat": self.lat,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )

            if response and response.get("status") == "success":
                self.progress.emit("Анализ успешно завершен!")
                self.finished.emit(response)
            else:
                error_msg = response.get("detail", "Неизвестная ошибка") if response else "Ошибка соединения с сервером"
                self.error.emit(error_msg)

        except Exception as e:
            self.error.emit(f"Ошибка при анализе поля: {str(e)}")

class FieldsLoaderWorker(QThread):
    """Поток для загрузки полей пользователя"""
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, make_request_func, token):
        super().__init__()
        self.make_request_func = make_request_func
        self.token = token

    def run(self):
        try:
            response = self.make_request_func("/givefield")
            if response and response.get("status") == "success":
                fields_data = response.get("keys", "")
                if fields_data:
                    try:
                        fields = json.loads(fields_data)
                        self.finished.emit(fields)
                    except json.JSONDecodeError:
                        self.finished.emit({})
                else:
                    self.finished.emit({})
            else:
                self.finished.emit({})
        except Exception as e:
            self.error.emit(f"Ошибка при загрузке полей: {str(e)}")

class FieldsSaverWorker(QThread):
    """Поток для сохранения полей пользователя"""
    finished = Signal(bool)
    error = Signal(str)

    def __init__(self, make_request_func, fields, token):
        super().__init__()
        self.make_request_func = make_request_func
        self.fields = fields
        self.token = token

    def run(self):
        try:
            fields_json = json.dumps(self.fields)
            response = self.make_request_func(
                "/savedata",
                method="POST",
                params={"key_array": fields_json}
            )
            success = bool(response and response.get("status") == "success")
            self.finished.emit(success)
        except Exception as e:
            self.error.emit(f"Ошибка при сохранении полей: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_token = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Устанавливаем название программы
        self.setWindowTitle("AgroAnalyzer")

        # Устанавливаем иконку
        self.set_app_icon()

        # Устанавливаем затемненный фон
        self.set_darkened_background()

        # Применяем стили с прозрачными элементами
        self.apply_styles()

        # Приватные переменные для хранения координат
        self._current_lat = None
        self._current_lng = None

        # Словарь для хранения полей (название -> координаты)
        self.fields = {}

        # Флаг авторизации пользователя
        self.is_authenticated = False

        # Обновляем отображение токена
        self.update_token_display()

        # Подключаем обработчики событий для кнопок
        self.setup_ui_connections()

        # Таймер для периодической синхронизации
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.auto_sync_fields)
        self.sync_timer.start(30000)  # Синхронизация каждые 30 секунд

    def set_app_icon(self):
        """Устанавливает иконку приложения"""
        icon_path = os.path.join(os.path.dirname(__file__), "app_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def set_darkened_background(self):
        """Устанавливает затемненный фон"""
        # Создаем QLabel для фона
        self.background_label = QLabel(self)
        self.background_label.setScaledContents(True)

        # Загружаем изображение
        background_path = os.path.join(os.path.dirname(__file__), "fon.jpg")
        if os.path.exists(background_path):
            pixmap = QPixmap(background_path)

            # Создаем затемненную версию изображения
            darkened_pixmap = self.darken_pixmap(pixmap, 0.6)  # 0.6 = уровень затемнения (60%)
            self.background_label.setPixmap(darkened_pixmap)
        else:
            # Если файла нет, создаем простой затемненный фон
            self.background_label.setStyleSheet("background-color: rgba(0, 0, 0, 0.7);")

        # Размещаем фон позади всех элементов
        self.background_label.lower()
        self.background_label.setGeometry(0, 0, self.width(), self.height())

        # Обработчик изменения размера окна
        self.resizeEvent = self.on_resize

    def darken_pixmap(self, pixmap, darkness=0.6):
        """Затемняет изображение"""
        result = QPixmap(pixmap.size())
        result.fill(Qt.transparent)

        painter = QPainter(result)
        painter.drawPixmap(0, 0, pixmap)

        # Рисуем полупрозрачный черный прямоугольник поверх изображения
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.fillRect(result.rect(), QColor(0, 0, 0, int(255 * darkness)))
        painter.end()

        return result

    def on_resize(self, event):
        """Обработчик изменения размера окна для подгонки фона"""
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def apply_styles(self):
        """Применяет CSS стили с прозрачными элементами"""
        style = """
        /* Прозрачный фон для главного окна */
        QMainWindow {
            background: transparent;
        }

        /* Прозрачный фон для центрального виджета */
        QWidget#centralwidget {
            background: transparent;
        }

        /* Полупрозрачные кнопки */
        QPushButton {
            border: 2px solid #2E8B57;
            border-radius: 15px;
            padding: 12px 20px;
            font-weight: bold;
            font-size: 20px;
            background-color: rgba(248, 248, 248, 0.85);
            color: #2E8B57;
            min-height: 25px;
        }

        QPushButton:hover {
            background-color: rgba(232, 232, 232, 0.95);
            border: 2px solid #228B22;
        }

        QPushButton:pressed {
            background-color: rgba(216, 216, 216, 0.95);
            border: 2px solid #006400;
        }

        /* Специальный стиль для кнопки анализа поля */
        QPushButton#pushButton_Anayze_field {
            background-color: rgba(50, 205, 50, 0.9);
            color: white;
            border: 2px solid #228B22;
            font-size: 20px;
            font-weight: bold;
            padding: 15px 25px;
            border-radius: 20px;
        }

        QPushButton#pushButton_Anayze_field:hover {
            background-color: rgba(40, 164, 40, 0.95);
            border: 2px solid #05ac4e;
        }

        QPushButton#pushButton_Anayze_field:pressed {
            background-color: rgba(30, 122, 30, 0.95);
            border: 2px solid #05ac4e;
        }

        /* Уменьшенные кнопки добавления и удаления поля */
        QPushButton#pushButton_add_field, QPushButton#pushButton_delite_field {
            max-width: 180px;
            min-width: 150px;
            padding: 8px 12px;
            font-size: 20px;
        }

        /* Прозрачные метки с легким фоном для читаемости */
        QLabel {
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 8px;
            color: white;
            font-weight: bold;
        }

        /* Специальный стиль для метки токена */
        QLabel#label_token {
            color: #87CEEB;
            font-weight: bold;
            padding: 10px;
            border: 2px solid rgba(135, 206, 235, 0.7);
            border-radius: 10px;
            background-color: rgba(240, 248, 255, 0.15);
            font-family: 'Courier New', monospace;
            font-size: 20px;
        }

        /* Специальный стиль для метки с координатами */
        QLabel#label_analyze {
            border: 2px solid rgba(50, 205, 50, 0.7);
            border-radius: 10px;
            padding: 10px;
            background-color: rgba(240, 255, 240, 0.15);
            color: #90EE90;
            font-weight: bold;
            font-size: 14px;
        }

        /* Стиль для метки истории */
        QLabel#label_history {
            border: 2px solid rgba(139, 69, 19, 0.7);
            border-radius: 10px;
            padding: 10px;
            background-color: rgba(255, 248, 220, 0.15);
            color: #DEB887;
            font-weight: bold;
            font-size: 14px;
        }

        QComboBox#comboBox_field {
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid #2E8B57;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                color: #2E8B57;
                font-weight: bold;
                min-width: 250px;
                min-height: 30px;
            }

        /* Прозрачные layouts */
        QHBoxLayout, QVBoxLayout {
            background: transparent;
        }
        """
        self.setStyleSheet(style)

    def update_token_display(self):
        """Обновляет отображение токена в label_token"""
        if hasattr(self.ui, 'label_token'):
            if self.user_token:
                self.ui.label_token.setText(f"Токен: {self.user_token}")
            else:
                self.ui.label_token.setText("Токен: не авторизован")

    def make_server_request(self, endpoint, method="GET", params=None, data=None):
        """Универсальный метод для выполнения запросов к серверу"""
        if not self.user_token and endpoint not in ["/get_token", "/add_user", "/health"]:
            print("Токен не установлен")
            return None

        base_url = "https://localhost:8000"
        try:
            url = f"{base_url}{endpoint}"

            # Создаем сессию с отключенной проверкой SSL
            session = requests.Session()
            session.verify = False

            # Добавляем токен в параметры, если его там нет и он доступен
            if params is None:
                params = {}
            if self.user_token and 'token' not in params and endpoint not in ["/get_token", "/add_user"]:
                params['token'] = self.user_token

            if method.upper() == "GET":
                response = session.get(url, params=params, timeout=10)
            elif method.upper() == "POST":
                response = session.post(url, params=params, data=data, timeout=10)
            elif method.upper() == "PUT":
                response = session.put(url, params=params, data=data, timeout=10)
            elif method.upper() == "DELETE":
                response = session.delete(url, params=params, timeout=10)
            else:
                return None

            if response.status_code == 200:
                return response.json()
            else:
                print(f"HTTP Error {response.status_code} for {url}: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Request error for {url}: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON decode error for {url}: {e}")
            return None

    def load_user_fields_from_server(self):
        """Асинхронно загружает поля пользователя с сервера"""
        if not self.user_token:
            print("Токен не установлен, невозможно загрузить поля")
            return

        # Показываем индикатор загрузки
        if hasattr(self.ui, 'label_history'):
            self.ui.label_history.setText("Загрузка полей...")

        # Запускаем асинхронную загрузку
        self.fields_loader = FieldsLoaderWorker(self.make_server_request, self.user_token)
        self.fields_loader.finished.connect(self.on_fields_loaded)
        self.fields_loader.error.connect(self.on_fields_load_error)
        self.fields_loader.start()

    def on_fields_loaded(self, fields):
        """Обрабатывает успешную загрузку полей"""
        self.fields = fields
        self.update_fields_combobox()
        print(f"Загружено {len(self.fields)} полей с сервера")

        if hasattr(self.ui, 'label_history'):
            self.ui.label_history.setText(f"Загружено {len(self.fields)} полей")

    def on_fields_load_error(self, error_msg):
        """Обрабатывает ошибку загрузки полей"""
        print(f"Ошибка при загрузке полей: {error_msg}")
        if hasattr(self.ui, 'label_history'):
            self.ui.label_history.setText("Ошибка загрузки полей")

    def save_fields_to_server(self):
        """Асинхронно сохраняет поля пользователя на сервер"""
        if not self.user_token:
            print("Токен не установлен, невозможно сохранить поля")
            return False

        # Запускаем асинхронное сохранение
        self.fields_saver = FieldsSaverWorker(self.make_server_request, self.fields, self.user_token)
        self.fields_saver.finished.connect(self.on_fields_saved)
        self.fields_saver.error.connect(self.on_fields_save_error)
        self.fields_saver.start()

        return True

    def on_fields_saved(self, success):
        """Обрабатывает результат сохранения полей"""
        if success:
            print("Поля успешно сохранены на сервере")
        else:
            print("Не удалось сохранить поля на сервере")

    def on_fields_save_error(self, error_msg):
        """Обрабатывает ошибку сохранения полей"""
        print(f"Ошибка при сохранении полей: {error_msg}")

    def auto_sync_fields(self):
        """Автоматическая синхронизация полей с сервером"""
        if self.is_authenticated and self.fields:
            self.save_fields_to_server()

    def update_fields_combobox(self):
        """Обновляет комбобокс полями из self.fields"""
        if hasattr(self.ui, 'comboBox_field'):
            self.ui.comboBox_field.clear()
            for field_name, coords in self.fields.items():
                if isinstance(coords, (list, tuple)) and len(coords) >= 2:
                    lat, lng = coords[0], coords[1]
                    field_text = f"{field_name} ({lat:.6f}, {lng:.6f})"
                    self.ui.comboBox_field.addItem(field_text)
                else:
                    print(f"Некорректные координаты для поля {field_name}: {coords}")

    def handle_map_click(self, lat, lng):
        """Обрабатывает клик по карте - получает координаты"""
        try:
            self._current_lat = lat
            self._current_lng = lng

            coordinates_text = f"Широта: {lat:.6f}, Долгота: {lng:.6f}"

            # Выводим координаты в label_analyze
            if hasattr(self.ui, 'label_analyze'):
                self.ui.label_analyze.setText(coordinates_text)
                self.ui.label_analyze.setStyleSheet("""
                    color: #90EE90;
                    font-weight: bold;
                    padding: 10px;
                    border: 2px solid rgba(50, 205, 50, 0.7);
                    border-radius: 10px;
                    background-color: rgba(240, 255, 240, 0.2);
                """)
                print("Координаты установлены в label_analyze")
            else:
                print("label_analyze не найден в UI")

            # Принудительно обновляем интерфейс
            QApplication.processEvents()

        except Exception as e:
            print(f"Ошибка в handle_map_click: {e}")

    def handle_add_field(self, field_name, lat, lng):
        """Обрабатывает добавление нового поля с названием и координатами"""
        try:
            # Сохраняем поле в словаре
            self.fields[field_name] = (lat, lng)

            # Обновляем комбобокс
            self.update_fields_combobox()

            # Устанавливаем текущий элемент в комбобоксе
            field_text = f"{field_name} ({lat:.6f}, {lng:.6f})"
            index = self.ui.comboBox_field.findText(field_text)
            if index >= 0:
                self.ui.comboBox_field.setCurrentIndex(index)

            # Обновляем историю
            if hasattr(self.ui, 'label_history'):
                history_text = f"Добавлено поле: {field_name}"
                self.ui.label_history.setText(history_text)

            # Асинхронно сохраняем на сервер
            if self.save_fields_to_server():
                print(f"Поле '{field_name}' отправлено на сохранение")
            else:
                self.show_message("Предупреждение", "Поле добавлено локально, но не сохранено на сервере", QMessageBox.Warning)

        except Exception as e:
            print(f"Ошибка в handle_add_field: {e}")
            self.show_message("Ошибка", f"Не удалось добавить поле: {str(e)}", QMessageBox.Critical)

    def setup_ui_connections(self):
        # Подключение кнопок входа и регистрации
        if hasattr(self.ui, 'login_main_button'):
            self.ui.login_main_button.clicked.connect(self.show_login_dialog)

        if hasattr(self.ui, 'register_main_button'):
            self.ui.register_main_button.clicked.connect(self.show_register_dialog)

        # Подключение кнопки анализа поля - теперь она отправляет запрос на анализ
        if hasattr(self.ui, 'pushButton_Anayze_field'):
            self.ui.pushButton_Anayze_field.clicked.connect(self.analyze_selected_field)

        # Подключение кнопки добавления поля
        if hasattr(self.ui, 'pushButton_add_field'):
            self.ui.pushButton_add_field.clicked.connect(self.open_map_for_add_field)

        # Подключение кнопки удаления поля
        if hasattr(self.ui, 'pushButton_delite_field'):
            self.ui.pushButton_delite_field.clicked.connect(self.delete_selected_field)

    def analyze_selected_field(self):
        """Асинхронно анализирует выбранное поле"""
        # Проверяем авторизацию
        if not self.is_authenticated:
            self.show_message("Предупреждение", "Войдите или зарегистрируйтесь", QMessageBox.Warning)
            return

        # Проверяем наличие добавленных полей
        if not self.fields:
            self.show_message("Предупреждение", "Добавьте поле", QMessageBox.Warning)
            return

        # Получаем выбранное поле из комбобокса
        current_index = self.ui.comboBox_field.currentIndex()
        if current_index < 0:
            self.show_message("Предупреждение", "Выберите поле для анализа", QMessageBox.Warning)
            return

        field_text = self.ui.comboBox_field.currentText()
        field_name = field_text.split(' (')[0]

        # Получаем координаты выбранного поля
        if field_name not in self.fields:
            self.show_message("Ошибка", f"Поле '{field_name}' не найдено", QMessageBox.Critical)
            return

        lat, lng = self.fields[field_name]

        # Создаем прогресс-диалог
        self.progress_dialog = QProgressDialog(f"Анализ поля '{field_name}'...", "Отмена", 0, 0, self)
        self.progress_dialog.setWindowTitle("Анализ поля")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.show()

        # Запускаем асинхронный анализ
        self.analysis_worker = AnalysisWorker(self.make_server_request, field_name, lat, lng, self.user_token)
        self.analysis_worker.finished.connect(self.on_analysis_finished)
        self.analysis_worker.error.connect(self.on_analysis_error)
        self.analysis_worker.progress.connect(self.on_analysis_progress)
        self.analysis_worker.start()

    def on_analysis_progress(self, message):
        """Обновляет прогресс анализа"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.setLabelText(message)

    def on_analysis_finished(self, response):
        """Обрабатывает завершение анализа"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.close()

        analysis_id = response.get("analysis_id")
        field_name = "выбранное поле"  # Можно получить из контекста

        self.show_message("Успех",
                         f"Анализ поля завершен!\n"
                         f"ID анализа: {analysis_id}",
                         QMessageBox.Information)

        # Обновляем историю
        if hasattr(self.ui, 'label_history'):
            self.ui.label_history.setText(f"Выполнен анализ поля")

        # Обновляем label_analyze с информацией о анализе
        if hasattr(self.ui, 'label_analyze'):
            self.ui.label_analyze.setText(f"Анализ выполнен успешно")
            self.ui.label_analyze.setStyleSheet("""
                color: #90EE90;
                font-weight: bold;
                padding: 10px;
                border: 2px solid rgba(50, 205, 50, 0.7);
                border-radius: 10px;
                background-color: rgba(240, 255, 240, 0.2);
            """)

    def on_analysis_error(self, error_msg):
        """Обрабатывает ошибку анализа"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.close()

        self.show_message("Ошибка",
                         f"Не удалось выполнить анализ поля: {error_msg}",
                         QMessageBox.Critical)

    def open_map_for_add_field(self):
         """Открывает карту для добавления нового поля"""
         # Проверяем авторизацию пользователя
         if not self.is_authenticated:
             self.show_message("Предупреждение",
                              "Войдите или зарегистрируйтесь",
                              QMessageBox.Warning)
             return

         # Создаем диалог с картой
         map_dialog = MapDialog(self, field_name_callback=self.handle_add_field)
         map_dialog.exec()

    def delete_selected_field(self):
        """Удаляет выбранное поле из комбобокса и с сервера"""
        # Проверяем авторизацию пользователя
        if not self.is_authenticated:
            self.show_message("Предупреждение",
                             "Войдите или зарегистрируйтесь",
                             QMessageBox.Warning)
            return

        try:
            current_index = self.ui.comboBox_field.currentIndex()
            if current_index >= 0:
                field_text = self.ui.comboBox_field.currentText()
                field_name = field_text.split(' (')[0]

                # Удаляем поле из словаря
                if field_name in self.fields:
                    del self.fields[field_name]

                # Удаляем поле из комбобокса
                self.ui.comboBox_field.removeItem(current_index)

                # Обновляем историю
                if hasattr(self.ui, 'label_history'):
                    history_text = f"Удалено поле: {field_name}"
                    self.ui.label_history.setText(history_text)

                # Асинхронно сохраняем изменения на сервер
                if self.save_fields_to_server():
                    self.show_message("Успех", f"Поле '{field_name}' удалено!", QMessageBox.Information)
                else:
                    self.show_message("Предупреждение", "Поле удалено локально, но не на сервере", QMessageBox.Warning)
            else:
                self.show_message("Предупреждение", "Нет выбранного поля для удаления", QMessageBox.Warning)

        except Exception as e:
            print(f"Ошибка при удалении поля: {e}")
            self.show_message("Ошибка", f"Не удалось удалить поле: {str(e)}", QMessageBox.Critical)

    def show_message(self, title, text, icon):
        """Показывает сообщение с увеличенным шрифтом и черным текстом"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)

        # Убираем иконку
        msg.setIcon(QMessageBox.NoIcon)

        # Увеличиваем размер шрифта
        font = QFont()
        font.setPointSize(11)
        msg.setFont(font)

        # Устанавливаем размер
        msg.setFixedSize(400, 200)

        # Применяем стили CSS с черным текстом
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
                min-width: 400px;
                min-height: 200px;
                color: black;
            }
            QMessageBox QLabel {
                color: black;
                font-size: 20px;
                min-width: 400px;
                min-height: 150px;
                qproperty-alignment: AlignCenter;
            }
            QMessageBox QPushButton {
                font-size: 20px;
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

        msg.updateGeometry()
        msg.exec()

    def show_login_dialog(self):
        """Показывает диалог входа"""
        dialog = LoginDialog(is_login=True, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.is_authenticated = True
            self.user_token = dialog.get_token()

            # Обновляем отображение токена
            self.update_token_display()

            # Обновляем историю
            if hasattr(self.ui, 'label_history'):
                self.ui.label_history.setText("Пользователь авторизован")

            # Асинхронно загружаем поля пользователя с сервера
            self.load_user_fields_from_server()

    def show_register_dialog(self):
        """Показывает диалог регистрации"""
        dialog = LoginDialog(is_login=False, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.is_authenticated = True
            self.user_token = dialog.get_token()

            # Обновляем отображение токена
            self.update_token_display()

            # Обновляем историю
            if hasattr(self.ui, 'label_history'):
                self.ui.label_history.setText("Пользователь зарегистрирован и авторизован")

            # Асинхронно загружаем поля пользователя с сервера (будет пусто для нового пользователя)
            self.load_user_fields_from_server()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Устанавливаем иконку для всего приложения
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "app_icon.ico")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
    except:
        pass

    widget = MainWindow()
    widget.showMaximized()
    sys.exit(app.exec())

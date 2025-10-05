# map.py
import requests
import io
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QMessageBox, QGraphicsView,
                               QGraphicsScene, QGraphicsPixmapItem, QGraphicsEllipseItem)
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QFont, QPixmap, QPainter, QPen, QColor, QBrush
import json
import os

class MapDialog(QDialog):
    def __init__(self, parent=None, field_name_callback=None):
        super().__init__(parent)
        self.field_name_callback = field_name_callback
        self.selected_lat = None
        self.selected_lng = None
        self.map_pixmap = None
        self.marker = None

        # Параметры карты мира
        self.min_lat = -90
        self.max_lat = 90
        self.min_lng = -180
        self.max_lng = 180

        self.setup_ui()
        self.load_map_image()

    def setup_ui(self):
        self.setWindowTitle("Выбор местоположения поля")
        self.resize(900, 600)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Инструкция
        instruction = QLabel("Кликните на карте для выбора местоположения поля")
        instruction.setAlignment(Qt.AlignCenter)
        instruction.setStyleSheet("font-weight: bold; font-size: 14px; color: #2E8B57; padding: 5px;")
        layout.addWidget(instruction)

        # Контейнер для карты и формы
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)

        # Левая часть - карта
        left_layout = QVBoxLayout()
        map_label = QLabel("Карта:")
        map_label.setStyleSheet("font-weight: bold; color: #333333;")
        left_layout.addWidget(map_label)

        # Создаем графическую сцену для карты
        self.map_view = QGraphicsView()
        self.map_view.setMinimumSize(600, 400)
        self.map_view.setRenderHint(QPainter.Antialiasing)
        self.map_scene = QGraphicsScene()
        self.map_view.setScene(self.map_scene)

        # Обработка кликов по карте
        self.map_view.mousePressEvent = self.handle_map_click

        left_layout.addWidget(self.map_view)

        # Правая часть - форма ввода
        right_layout = QVBoxLayout()

        # Поле для названия
        name_layout = QVBoxLayout()
        name_label = QLabel("Название поля:")
        name_label.setStyleSheet("font-weight: bold; color: #333333;")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите название поля")
        self.name_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #CCCCCC;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #32CD32;
            }
        """)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        right_layout.addLayout(name_layout)

        # Координаты
        coord_layout = QVBoxLayout()
        coord_label = QLabel("Выбранные координаты:")
        coord_label.setStyleSheet("font-weight: bold; color: #333333; margin-top: 10px;")

        lat_layout = QHBoxLayout()
        lat_label = QLabel("Широта:")
        lat_label.setFixedWidth(50)
        self.lat_edit = QLineEdit()
        self.lat_edit.setPlaceholderText("Кликните на карте")
        self.lat_edit.setReadOnly(False)
        self.lat_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
        """)
        lat_layout.addWidget(lat_label)
        lat_layout.addWidget(self.lat_edit)

        lng_layout = QHBoxLayout()
        lng_label = QLabel("Долгота:")
        lng_label.setFixedWidth(50)
        self.lng_edit = QLineEdit()
        self.lng_edit.setPlaceholderText("Кликните на карте")
        self.lng_edit.setReadOnly(False)
        self.lng_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
        """)
        lng_layout.addWidget(lng_label)
        lng_layout.addWidget(self.lng_edit)

        coord_layout.addWidget(coord_label)
        coord_layout.addLayout(lat_layout)
        coord_layout.addLayout(lng_layout)
        right_layout.addLayout(coord_layout)

        # Статус выбора
        self.status_label = QLabel("Статус: Не выбрано")
        self.status_label.setStyleSheet("color: #666666; font-size: 12px; padding: 8px; background-color: #fff3cd; border-radius: 4px; border: 1px solid #ffeaa7; margin-top: 10px;")
        right_layout.addWidget(self.status_label)

        # Подсказка
        hint_label = QLabel(
            '• Кликните на карте для выбора местоположения\n'
            '• Или введите координаты вручную\n'
            '• Для точного выбора используйте:\n'
            '  https://yandex.ru/maps/\n'
            '  https://google.com/maps'
        )
        hint_label.setStyleSheet("color: #666666; font-size: 11px; padding: 10px; background-color: #f9f9f9; border-radius: 5px; border: 1px solid #e0e0e0; margin-top: 10px;")
        hint_label.setWordWrap(True)
        right_layout.addWidget(hint_label)

        right_layout.addStretch()

        content_layout.addLayout(left_layout)
        content_layout.addLayout(right_layout)
        layout.addLayout(content_layout)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.ok_button = QPushButton("Добавить поле")
        self.ok_button.setMinimumHeight(35)
        self.ok_button.setEnabled(True)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #32CD32;
                color: white;
                border: 2px solid #228B22;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #28A428;
                border: 2px solid #1E7A1E;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                border: 2px solid #999999;
                color: #666666;
            }
        """)
        self.ok_button.clicked.connect(self.add_field)

        cancel_button = QPushButton("Отмена")
        cancel_button.setMinimumHeight(35)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #F8F8F8;
                color: #2E8B57;
                border: 2px solid #2E8B57;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #E8E8E8;
            }
        """)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_map_image(self):
        """Создает простую схематическую карту"""
        # Создаем изображение карты
        pixmap = QPixmap(800, 500)
        pixmap.fill(QColor(240, 248, 255))  # Светло-голубой фон

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Рисуем контур карты
        painter.setPen(QPen(QColor(100, 149, 237), 2))  # Cornflower blue
        painter.drawRect(10, 10, 780, 480)

        # Рисуем континенты упрощенно
        painter.setPen(QPen(QColor(34, 139, 34), 1))  # Forest green
        painter.setBrush(QBrush(QColor(144, 238, 144)))  # Light green

        # Европа/Азия
        europe_path = [
            QPointF(350, 150), QPointF(400, 140), QPointF(450, 160),
            QPointF(500, 180), QPointF(550, 200), QPointF(600, 220),
            QPointF(650, 250), QPointF(650, 300), QPointF(600, 350),
            QPointF(550, 380), QPointF(500, 400), QPointF(450, 420),
            QPointF(400, 430), QPointF(350, 440), QPointF(300, 430),
            QPointF(250, 420), QPointF(200, 400), QPointF(150, 380),
            QPointF(100, 350), QPointF(50, 300), QPointF(50, 250),
            QPointF(100, 200), QPointF(150, 180), QPointF(200, 160),
            QPointF(250, 150), QPointF(300, 140)
        ]

        for i in range(len(europe_path) - 1):
            painter.drawLine(europe_path[i], europe_path[i+1])

        # Подписи
        painter.setPen(QPen(Qt.black, 1))
        painter.drawText(400, 200, "Европа")
        painter.drawText(500, 300, "Азия")
        painter.drawText(200, 100, "Россия")

        # Сетка координат
        painter.setPen(QPen(QColor(200, 200, 200), 0.5))
        for x in range(50, 800, 50):
            painter.drawLine(x, 10, x, 490)
        for y in range(50, 500, 50):
            painter.drawLine(10, y, 790, y)

        painter.end()

        self.map_pixmap = pixmap
        self.display_map()

    def display_map(self):
        """Отображает карту в графической сцене"""
        if self.map_pixmap:
            self.map_scene.clear()
            pixmap_item = QGraphicsPixmapItem(self.map_pixmap)
            self.map_scene.addItem(pixmap_item)
            self.map_view.setSceneRect(0, 0, self.map_pixmap.width(), self.map_pixmap.height())

    def handle_map_click(self, event):
        """Обрабатывает клик по карте"""
        try:
            # Получаем координаты клика относительно карты
            scene_pos = self.map_view.mapToScene(event.pos())

            # Преобразуем координаты клика в географические координаты
            map_width = self.map_pixmap.width()
            map_height = self.map_pixmap.height()

            # Простое линейное преобразование
            x_ratio = scene_pos.x() / map_width
            y_ratio = scene_pos.y() / map_height

            # Преобразуем в географические координаты
            lat = self.max_lat - (y_ratio * (self.max_lat - self.min_lat))
            lng = self.min_lng + (x_ratio * (self.max_lng - self.min_lng))

            # Ограничиваем координаты разумными значениями
            lat = max(min(lat, self.max_lat), self.min_lat)
            lng = max(min(lng, self.max_lng), self.min_lng)

            self.selected_lat = lat
            self.selected_lng = lng

            # Обновляем поля координат
            self.lat_edit.setText(f"{lat:.6f}")
            self.lng_edit.setText(f"{lng:.6f}")

            # Обновляем статус
            self.status_label.setText("Статус: Местоположение выбрано")
            self.status_label.setStyleSheet("color: #155724; font-size: 12px; padding: 8px; background-color: #d4edda; border-radius: 4px; border: 1px solid #c3e6cb;")

            # Добавляем маркер на карту
            self.add_marker(scene_pos.x(), scene_pos.y())

        except Exception as e:
            print(f"Ошибка обработки клика: {e}")

    def add_marker(self, x, y):
        """Добавляет маркер на карту в указанные координаты"""
        # Удаляем старый маркер
        if self.marker:
            self.map_scene.removeItem(self.marker)

        # Создаем новый маркер
        marker_size = 10
        self.marker = QGraphicsEllipseItem(x - marker_size/2, y - marker_size/2,
                                         marker_size, marker_size)
        self.marker.setPen(QPen(Qt.black, 1))
        self.marker.setBrush(QBrush(QColor(255, 0, 0)))
        self.map_scene.addItem(self.marker)

    def add_field(self):
        """Добавляет поле с введенными координатами"""
        field_name = self.name_edit.text().strip()

        if not field_name:
            self.show_message("Ошибка", "Введите название поля", QMessageBox.Warning)
            self.name_edit.setFocus()
            return

        # Получаем координаты из полей ввода
        lat_text = self.lat_edit.text().strip()
        lng_text = self.lng_edit.text().strip()

        if not lat_text or not lng_text:
            self.show_message("Ошибка", "Введите координаты поля", QMessageBox.Warning)
            return

        try:
            lat = float(lat_text.replace(',', '.'))
            lng = float(lng_text.replace(',', '.'))
        except ValueError:
            self.show_message("Ошибка", "Координаты должны быть числами", QMessageBox.Warning)
            return

        # Проверка валидности координат
        if not (-90 <= lat <= 90):
            self.show_message("Ошибка", "Широта должна быть в диапазоне от -90 до 90", QMessageBox.Warning)
            self.lat_edit.setFocus()
            return

        if not (-180 <= lng <= 180):
            self.show_message("Ошибка", "Долгота должна быть в диапазоне от -180 до 180", QMessageBox.Warning)
            self.lng_edit.setFocus()
            return

        # Вызываем callback для добавления поля
        if self.field_name_callback:
            self.field_name_callback(field_name, lat, lng)

        self.accept()

    def show_message(self, title, text, icon):
        """Показывает сообщение об ошибке"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(icon)

        font = QFont()
        font.setPointSize(11)
        msg.setFont(font)

        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
                color: black;
            }
            QMessageBox QLabel {
                color: black;
                font-size: 12px;
            }
            QMessageBox QPushButton {
                background-color: #f0f0f0;
                color: black;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 12px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)

        msg.exec()

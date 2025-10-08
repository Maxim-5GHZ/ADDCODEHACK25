from PySide6.QtCore import Qt, QUrl, QTimer, QPointF, Signal
from PySide6.QtCore import QObject, Slot
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWidgets import (QVBoxLayout, QWidget, QDialog, QHBoxLayout,
                              QLabel, QLineEdit, QPushButton, QMessageBox,
                              QComboBox, QGroupBox)
from PySide6.QtGui import QFont
import math

class MapBridge(QObject):
    """Мост для взаимодействия между Python и JavaScript"""
    coordinateSelected = Signal(float, float)
    areaSelected = Signal(list)  # Сигнал для передачи координат области
    pointRadiusSelected = Signal(float, float, float)  # Сигнал для точки и радиуса

    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot(float, float)
    def onCoordinateSelected(self, lat, lng):
        """Вызывается из JavaScript при выборе координат"""
        self.coordinateSelected.emit(lat, lng)

    @Slot(list)
    def onAreaSelected(self, coordinates):
        """Вызывается из JavaScript при изменении области"""
        self.areaSelected.emit(coordinates)

    @Slot(float, float, float)
    def onPointRadiusSelected(self, lat, lng, radius):
        """Вызывается из JavaScript при выборе точки и радиуса"""
        self.pointRadiusSelected.emit(lat, lng, radius)

class MapWidget(QWidget):
    """Виджет для отображения интерактивной карты OpenStreetMap с выбором области или точки с радиусом"""

    coordinateSelected = Signal(float, float)
    areaSelected = Signal(list)
    pointRadiusSelected = Signal(float, float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.bridge = MapBridge()
        self.bridge.coordinateSelected.connect(self.coordinateSelected)
        self.bridge.areaSelected.connect(self.areaSelected)
        self.bridge.pointRadiusSelected.connect(self.pointRadiusSelected)

        self.setup_ui()
        self.setup_map()

        self.map_dialog = parent
        self.current_mode = "area"  # По умолчанию режим области

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        layout = QVBoxLayout(self)

        # WebView для отображения карты
        self.web_view = QWebEngineView()
        self.web_view.setMinimumSize(600, 400)

        # Настройка WebChannel для взаимодействия с JavaScript
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)

        layout.addWidget(self.web_view)
        self.setLayout(layout)

    def setup_map(self):
        """Настройка карты OpenStreetMap с Leaflet с поддержкой двух режимов"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Выбор области или точки с радиусом</title>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0">

            <!-- Leaflet CSS -->
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />

            <style>
                #map {
                    height: 100%;
                    width: 100%;
                    border-radius: 10px;
                }
                html, body {
                    height: 100%;
                    margin: 0;
                    padding: 0;
                    font-family: Arial, sans-serif;
                }
                .coordinates-info {
                    position: absolute;
                    top: 10px;
                    right: 10px;
                    background: white;
                    padding: 10px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.2);
                    z-index: 1000;
                    font-size: 12px;
                }
                .area-info {
                    position: absolute;
                    top: 10px;
                    left: 10px;
                    background: white;
                    padding: 10px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.2);
                    z-index: 1000;
                    font-size: 12px;
                    max-width: 300px;
                }
                .radius-control {
                    position: absolute;
                    bottom: 10px;
                    left: 10px;
                    background: white;
                    padding: 10px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.2);
                    z-index: 1000;
                }
            </style>
        </head>
        <body>
            <div class="area-info" id="areaInfo">
                <strong>Выбор области</strong><br>
                Перетащите угловые маркеры для определения границ поля
            </div>
            <div class="coordinates-info" id="coordinatesInfo">
                Координаты: не выбраны
            </div>
            <div class="radius-control" id="radiusControl" style="display: none;">
                <strong>Управление радиусом</strong><br>
                <label>Радиус: <span id="radiusValue">1000</span> м</label><br>
                <input type="range" id="radiusSlider" min="100" max="5000" step="100" value="1000" oninput="updateRadius(this.value)" style="width: 200px;">
            </div>
            <div id="map"></div>

            <!-- Leaflet JavaScript -->
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

            <!-- Qt WebChannel -->
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>

            <script>
                var map;
                var cornerMarkers = [];
                var areaPolygon;
                var centerMarker;
                var radiusCircle;
                var currentRadius = 1000;
                var bridge;
                var currentMode = 'area';

                // Инициализация WebChannel
                new QWebChannel(qt.webChannelTransport, function(channel) {
                    bridge = channel.objects.bridge;
                });

                // Функция инициализации карта
                function initMap() {
                    // Создаем карту с центром в Москве
                    map = L.map('map').setView([55.7558, 37.6173], 10);

                    // Добавляем слой OpenStreetMap
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        attribution: '© OpenStreetMap contributors',
                        maxZoom: 18
                    }).addTo(map);

                    // Инициализируем режим области
                    initAreaMode();
                }

                // Функция инициализации режима области
                function initAreaMode() {
                    // Создаем начальные координаты для 4 углов (прямоугольник 2x2 км)
                    var centerLat = 55.7558;
                    var centerLng = 37.6173;
                    var delta = 0.01; // Примерно 1.1 км

                    var corners = [
                        [centerLat - delta, centerLng - delta], // Северо-запад
                        [centerLat - delta, centerLng + delta], // Северо-восток
                        [centerLat + delta, centerLng + delta], // Юго-восток
                        [centerLat + delta, centerLng - delta]  // Юго-запад
                    ];

                    // Создаем полигон области
                    areaPolygon = L.polygon(corners, {
                        color: 'blue',
                        weight: 2,
                        fillColor: 'lightblue',
                        fillOpacity: 0.4,
                        opacity: 0.8
                    }).addTo(map);

                    // Создаем 4 угловых маркера
                    for (var i = 0; i < 4; i++) {
                        var marker = L.marker(corners[i], {
                            draggable: true,
                            icon: L.divIcon({
                                className: 'corner-marker',
                                html: '<div style="background-color: red; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>',
                                iconSize: [16, 16],
                                iconAnchor: [8, 8]
                            })
                        }).addTo(map);

                        // Добавляем обработчик перетаскивания для маркера
                        marker.on('drag', function(e) {
                            updateArea();
                        });

                        cornerMarkers.push(marker);
                    }

                    // Обновляем информацию об области
                    updateAreaInfo();

                    // Добавляем обработчик кликов по карте для перемещения всей области
                    map.on('click', function(e) {
                        if (currentMode === 'area') {
                            // При клике на карте перемещаем всю область в это место
                            var newCenter = e.latlng;
                            var bounds = areaPolygon.getBounds();
                            var currentCenter = bounds.getCenter();
                            var latDiff = newCenter.lat - currentCenter.lat;
                            var lngDiff = newCenter.lng - currentCenter.lng;

                            // Перемещаем все маркеры
                            for (var i = 0; i < cornerMarkers.length; i++) {
                                var oldLatLng = cornerMarkers[i].getLatLng();
                                cornerMarkers[i].setLatLng([oldLatLng.lat + latDiff, oldLatLng.lng + lngDiff]);
                            }

                            updateArea();
                        }
                    });
                }

                // Функция инициализации режима точки и радиуса
                function initPointRadiusMode() {
                    var centerLat = 55.7558;
                    var centerLng = 37.6173;

                    // Создаем центральный маркер
                    centerMarker = L.marker([centerLat, centerLng], {
                        draggable: true
                    }).addTo(map);

                    // Создаем круг
                    radiusCircle = L.circle([centerLat, centerLng], {
                        color: 'red',
                        fillColor: '#f03',
                        fillOpacity: 0.3,
                        radius: currentRadius
                    }).addTo(map);

                    // Обработчик перетаскивания маркера
                    centerMarker.on('drag', function(e) {
                        var newCenter = centerMarker.getLatLng();
                        radiusCircle.setLatLng(newCenter);
                        updatePointRadiusInfo();

                        // Отправляем данные в Python
                        if (bridge) {
                            bridge.onPointRadiusSelected(newCenter.lat, newCenter.lng, currentRadius);
                        }
                    });

                    // Обработчик клика по карте для перемещения центра
                    map.on('click', function(e) {
                        if (currentMode === 'point') {
                            centerMarker.setLatLng(e.latlng);
                            radiusCircle.setLatLng(e.latlng);
                            updatePointRadiusInfo();

                            // Отправляем данные в Python
                            if (bridge) {
                                bridge.onPointRadiusSelected(e.latlng.lat, e.latlng.lng, currentRadius);
                            }
                        }
                    });

                    updatePointRadiusInfo();
                }

                // Функция обновления области при перемещении маркеров
                function updateArea() {
                    var newCorners = [];
                    for (var i = 0; i < cornerMarkers.length; i++) {
                        var latLng = cornerMarkers[i].getLatLng();
                        newCorners.push([latLng.lat, latLng.lng]);
                    }

                    // Обновляем полигон
                    areaPolygon.setLatLngs(newCorners);

                    // Обновляем информацию
                    updateAreaInfo();

                    // Отправляем координаты в Python
                    if (bridge) {
                        bridge.onAreaSelected(newCorners);
                    }
                }

                // Функция обновления информации об области
                function updateAreaInfo() {
                    var bounds = areaPolygon.getBounds();
                    var center = bounds.getCenter();
                    var area = calculateArea(cornerMarkers);

                    var info = "Режим: Область<br>Центр: " + center.lat.toFixed(6) + ", " + center.lng.toFixed(6) +
                              "<br>Примерная площадь: " + area.toFixed(2) + " га";

                    document.getElementById('coordinatesInfo').innerHTML = info;
                }

                // Функция обновления информации о точке и радиусе
                function updatePointRadiusInfo() {
                    var center = centerMarker.getLatLng();
                    var area = Math.PI * Math.pow(currentRadius / 1000, 2); // Площадь в км²
                    var areaHectares = area * 100; // Площадь в гектарах

                    var info = "Режим: Точка и радиус<br>Центр: " + center.lat.toFixed(6) + ", " + center.lng.toFixed(6) +
                              "<br>Радиус: " + currentRadius + " м" +
                              "<br>Примерная площадь: " + areaHectares.toFixed(2) + " га";

                    document.getElementById('coordinatesInfo').innerHTML = info;
                }

                // Функция для расчета примерной площади в гектарах
                function calculateArea(markers) {
                    if (markers.length < 3) return 0;

                    var area = 0;
                    var n = markers.length;

                    for (var i = 0; i < n; i++) {
                        var j = (i + 1) % n;
                        var p1 = markers[i].getLatLng();
                        var p2 = markers[j].getLatLng();

                        // Простой расчет площади (для небольших областей на сфере)
                        area += p1.lng * p2.lat - p2.lng * p1.lat;
                    }

                    area = Math.abs(area) / 2.0;

                    // Конвертация в гектары (приблизительно)
                    // 1 градус широты ≈ 111 км, 1 градус долготы ≈ 111 км * cos(широта)
                    var centerLat = (markers[0].getLatLng().lat + markers[2].getLatLng().lat) / 2;
                    var latToKm = 111.0;
                    var lngToKm = 111.0 * Math.cos(centerLat * Math.PI / 180);

                    // Площадь в квадратных километрах, затем в гектары
                    var areaSqKm = area * latToKm * lngToKm;
                    var areaHectares = areaSqKm * 100;

                    return areaHectares;
                }

                // Функция смены режима
                function changeMode(mode) {
                    currentMode = mode;

                    // Очищаем карту от предыдущих элементов
                    if (areaPolygon) map.removeLayer(areaPolygon);
                    if (centerMarker) map.removeLayer(centerMarker);
                    if (radiusCircle) map.removeLayer(radiusCircle);

                    for (var i = 0; i < cornerMarkers.length; i++) {
                        map.removeLayer(cornerMarkers[i]);
                    }
                    cornerMarkers = [];

                    // Показываем/скрываем элементы управления радиусом
                    var radiusControl = document.getElementById('radiusControl');
                    var areaInfo = document.getElementById('areaInfo');

                    if (mode === 'area') {
                        radiusControl.style.display = 'none';
                        areaInfo.innerHTML = '<strong>Выбор области</strong><br>Перетащите угловые маркеры для определения границ поля';
                        initAreaMode();
                    } else if (mode === 'point') {
                        radiusControl.style.display = 'block';
                        areaInfo.innerHTML = '<strong>Выбор точки и радиуса</strong><br>Перетащите центральный маркер или кликните на карте';
                        initPointRadiusMode();
                    }
                }

                // Функция обновления радиуса
                function updateRadius(radius) {
                    currentRadius = parseInt(radius);
                    document.getElementById('radiusValue').innerText = currentRadius;

                    if (radiusCircle) {
                        radiusCircle.setRadius(currentRadius);
                        updatePointRadiusInfo();

                        // Отправляем данные в Python
                        if (bridge && centerMarker) {
                            var center = centerMarker.getLatLng();
                            bridge.onPointRadiusSelected(center.lat, center.lng, currentRadius);
                        }
                    }
                }

                // Функция для установки области из Python
                function setArea(coordinates) {
                    if (coordinates.length !== 4) return;

                    // Обновляем позиции маркеров
                    for (var i = 0; i < 4; i++) {
                        cornerMarkers[i].setLatLng([coordinates[i][0], coordinates[i][1]]);
                    }

                    updateArea();

                    // Центрируем карту на области
                    var bounds = L.latLngBounds(coordinates);
                    map.fitBounds(bounds);
                }

                // Функция для установки точки и радиуса из Python
                function setPointRadius(lat, lng, radius) {
                    if (centerMarker && radiusCircle) {
                        centerMarker.setLatLng([lat, lng]);
                        radiusCircle.setLatLng([lat, lng]);
                        radiusCircle.setRadius(radius);

                        currentRadius = radius;
                        document.getElementById('radiusSlider').value = radius;
                        document.getElementById('radiusValue').innerText = radius;

                        updatePointRadiusInfo();
                    }
                }

                // Инициализируем карту после загрузки страницы
                document.addEventListener('DOMContentLoaded', initMap);
            </script>
        </body>
        </html>
        """

        # Загружаем HTML в WebView
        self.web_view.setHtml(html_content)

    def set_mode(self, mode):
        """Установить режим работы карты"""
        self.current_mode = mode
        js_code = f"changeMode('{mode}');"
        self.web_view.page().runJavaScript(js_code)

    def set_area(self, coordinates):
        """Установить область на карте из Python"""
        if len(coordinates) != 4:
            return

        js_code = f"setArea({coordinates});"
        self.web_view.page().runJavaScript(js_code)

    def set_point_radius(self, lat, lng, radius):
        """Установить точку и радиус на карте из Python"""
        js_code = f"setPointRadius({lat}, {lng}, {radius});"
        self.web_view.page().runJavaScript(js_code)

class MapDialog(QDialog):
    """Диалог для выбора области или точки с радиусом на карте"""

    def __init__(self, parent=None, field_name_callback=None):
        super().__init__(parent)
        self.field_name_callback = field_name_callback
        self.selected_coordinates = None  # Для режима области
        self.selected_point_radius = None  # Для режима точки и радиуса (lat, lng, radius)
        self.current_mode = "area"  # Текущий режим

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Выбор области или точки с радиусом")
        self.resize(1200, 800)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Заголовок
        title_label = QLabel("Выбор области поля")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-weight: bold;
            font-size: 18px;
            color: #2E8B57;
            padding: 10px;
            background-color: #f8fff8;
            border-radius: 8px;
            border: 2px solid #2E8B57;
        """)
        layout.addWidget(title_label)

        # Основной контент
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)

        # Левая часть - карта
        left_layout = QVBoxLayout()
        left_layout.setSpacing(8)

        map_header = QLabel("Интерактивная карта:")
        map_header.setStyleSheet("font-weight: bold; color: #333333; font-size: 14px;")
        left_layout.addWidget(map_header)

        # Используем WebEngineView для карты
        self.map_view = MapWidget(self)
        self.map_view.areaSelected.connect(self.handle_area_selected)
        self.map_view.pointRadiusSelected.connect(self.handle_point_radius_selected)
        self.map_view.setMinimumSize(800, 500)
        left_layout.addWidget(self.map_view)

        # Инструкция по использованию карты
        map_instructions = QLabel(
            "• Выберите режим: область или точка с радиусом\n"
            "• Для области: перетащите маркеры для определения границ\n"
            "• Для точки с радиуса: перетащите центральный маркер или кликните на карте\n"
            "• Используйте слайдер на карте для изменения радиуса\n"
            "• Используйте колесо мыши для масштабирования карты"
        )
        map_instructions.setStyleSheet("""
            color: #666666;
            font-size: 12px;
            padding: 8px;
            background-color: #f9f9f9;
            border-radius: 5px;
            border: 1px solid #e0e0e0;
        """)
        map_instructions.setWordWrap(True)
        left_layout.addWidget(map_instructions)

        content_layout.addLayout(left_layout)

        # Правая часть - форма
        right_layout = QVBoxLayout()
        right_layout.setSpacing(12)

        # Название поля
        name_group = QVBoxLayout()
        name_label = QLabel("Название поля:")
        name_label.setStyleSheet("font-weight: bold; color: #333333; font-size: 14px;")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите уникальное название поля")
        self.name_edit.textChanged.connect(self.check_form_validity)
        self.name_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #CCCCCC;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #32CD32;
                background-color: #f8fff8;
            }
        """)
        name_group.addWidget(name_label)
        name_group.addWidget(self.name_edit)
        right_layout.addLayout(name_group)

        # Выбор режима
        mode_group = QVBoxLayout()
        mode_label = QLabel("Режим выбора:")
        mode_label.setStyleSheet("font-weight: bold; color: #333333; font-size: 14px; margin-top: 10px;")

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Область (4 точки)", "area")
        self.mode_combo.addItem("Точка и радиус", "point")
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        self.mode_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #CCCCCC;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
        """)

        mode_group.addWidget(mode_label)
        mode_group.addWidget(self.mode_combo)
        right_layout.addLayout(mode_group)

        # Группа для координат области
        self.area_group = QGroupBox("Координаты области")
        self.area_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #CCCCCC;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        area_layout = QVBoxLayout()

        # Поля для координат 4 точек
        self.coord_edits = []
        point_names = ["Северо-запад", "Северо-восток", "Юго-восток", "Юго-запад"]

        for i, point_name in enumerate(point_names):
            point_layout = QHBoxLayout()
            point_label = QLabel(f"{point_name}:")
            point_label.setFixedWidth(100)
            point_label.setStyleSheet("font-weight: bold;")

            coord_edit = QLineEdit()
            coord_edit.setPlaceholderText("широта, долгота")
            coord_edit.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #CCCCCC;
                    border-radius: 5px;
                    padding: 6px;
                    font-size: 12px;
                    background-color: #f8f8f8;
                }
            """)
            coord_edit.setReadOnly(True)  # Только для чтения, изменяется через карту

            point_layout.addWidget(point_label)
            point_layout.addWidget(coord_edit)
            area_layout.addLayout(point_layout)
            self.coord_edits.append(coord_edit)

        self.area_group.setLayout(area_layout)
        right_layout.addWidget(self.area_group)

        # Информация об области
        self.area_info = QLabel("Область не выбрана")
        self.area_info.setStyleSheet("""
            color: #2E8B57;
            font-weight: bold;
            padding: 8px;
            border: 1px solid #2E8B57;
            border-radius: 5px;
            background-color: #f8fff8;
        """)
        self.area_info.setWordWrap(True)
        right_layout.addWidget(self.area_info)

        right_layout.addStretch()
        content_layout.addLayout(right_layout)
        layout.addLayout(content_layout)

        # Кнопки действий
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.ok_button = QPushButton("Добавить поле")
        self.ok_button.setMinimumHeight(40)
        self.ok_button.setEnabled(False)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #32CD32;
                color: white;
                border: 2px solid #228B22;
                border-radius: 8px;
                padding: 10px 20px;
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
        cancel_button.setMinimumHeight(40)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #F8F8F8;
                color: #FF4444;
                border: 2px solid #FF4444;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #FFE8E8;
            }
        """)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def on_mode_changed(self, index):
        """Обрабатывает изменение режима"""
        self.current_mode = self.mode_combo.currentData()

        # Показываем/скрываем соответствующие группы
        if self.current_mode == "area":
            self.area_group.setVisible(True)
        else:  # point
            self.area_group.setVisible(False)

        # Устанавливаем режим на карте
        self.map_view.set_mode(self.current_mode)

        # Сбрасываем выбранные данные
        self.selected_coordinates = None
        self.selected_point_radius = None
        self.check_form_validity()

    def handle_area_selected(self, coordinates):
        """Обрабатывает выбор области на карте"""
        try:
            if self.current_mode != "area":
                return

            self.selected_coordinates = coordinates
            self.selected_point_radius = None

            # Обновляем поля координат
            point_names = ["Северо-запад", "Северо-восток", "Юго-восток", "Юго-запад"]
            for i, (lat, lng) in enumerate(coordinates):
                if i < len(self.coord_edits):
                    self.coord_edits[i].setText(f"{lat:.6f}, {lng:.6f}")

            # Вычисляем центр области
            center_lat = sum(coord[0] for coord in coordinates) / 4
            center_lng = sum(coord[1] for coord in coordinates) / 4

            # Вычисляем примерную площадь
            area = self.calculate_area(coordinates)

            # Обновляем информацию об области
            area_text = f"Режим: Область\nЦентр: {center_lat:.6f}, {center_lng:.6f}\nПримерная площадь: {area:.2f} га"
            self.area_info.setText(area_text)

            # Активируем кнопку OK если есть название поля
            self.check_form_validity()

        except Exception as e:
            print(f"Ошибка в handle_area_selected: {e}")

    def handle_point_radius_selected(self, lat, lng, radius):
        """Обрабатывает выбор точки и радиуса на карте"""
        try:
            if self.current_mode != "point":
                return

            self.selected_point_radius = (lat, lng, radius)
            self.selected_coordinates = None

            # Вычисляем примерную площадь
            area = math.pi * (radius / 1000) ** 2 * 100  # Площадь в гектарах

            # Обновляем информацию
            area_text = f"Режим: Точка и радиус\nЦентр: {lat:.6f}, {lng:.6f}\nРадиус: {radius} м\nПримерная площадь: {area:.2f} га"
            self.area_info.setText(area_text)

            # Активируем кнопку OK если есть название поля
            self.check_form_validity()

        except Exception as e:
            print(f"Ошибка в handle_point_radius_selected: {e}")

    def calculate_area(self, coordinates):
        """Вычисляет примерную площадь области в гектарах"""
        if len(coordinates) != 4:
            return 0

        # Простой расчет площади для прямоугольной области
        lat_coords = [coord[0] for coord in coordinates]
        lng_coords = [coord[1] for coord in coordinates]

        lat_min, lat_max = min(lat_coords), max(lat_coords)
        lng_min, lng_max = min(lng_coords), max(lng_coords)

        # Расчет площади в квадратных градусах
        area_deg = (lat_max - lat_min) * (lng_max - lng_min)

        # Приблизительная конвертация в гектары
        # 1 градус широты ≈ 111 км, 1 градус долготы ≈ 111 км * cos(широта)
        center_lat = sum(lat_coords) / 4
        lat_to_km = 111.0
        lng_to_km = 111.0 * abs(math.cos(math.radians(center_lat)))

        # Площадь в квадратных километрах, затем в гектары
        area_sq_km = area_deg * lat_to_km * lng_to_km
        area_hectares = area_sq_km * 100

        return area_hectares

    def check_form_validity(self):
        """Проверяет валидность формы"""
        has_name = bool(self.name_edit.text().strip())

        if self.current_mode == "area":
            has_data = self.selected_coordinates is not None
        else:  # point
            has_data = self.selected_point_radius is not None

        self.ok_button.setEnabled(has_name and has_data)

    def add_field(self):
        """Добавляет поле с введенными данными"""
        field_name = self.name_edit.text().strip()

        if not field_name:
            self.show_message("Ошибка", "Введите название поля", QMessageBox.Warning)
            self.name_edit.setFocus()
            return

        if self.current_mode == "area":
            if self.selected_coordinates is None:
                self.show_message("Ошибка", "Выберите область на карте", QMessageBox.Warning)
                return

            # Проверяем валидность координат
            for lat, lng in self.selected_coordinates:
                if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                    self.show_message("Ошибка", "Некорректные координаты области", QMessageBox.Warning)
                    return

            # Вызываем callback для добавления поля (через parent - MainWindow)
            if self.field_name_callback:
                # Передаем название поля и все 4 точки области
                self.field_name_callback(field_name, self.selected_coordinates)

        else:  # point mode
            if self.selected_point_radius is None:
                self.show_message("Ошибка", "Выберите точку и радиус на карте", QMessageBox.Warning)
                return

            lat, lng, radius = self.selected_point_radius

            # Проверяем валидность координат
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                self.show_message("Ошибка", "Некорректные координаты точки", QMessageBox.Warning)
                return

            # Вызываем callback для добавления поля (через parent - MainWindow)
            if self.field_name_callback:
                # Передаем название поля и данные точки с радиусом
                self.field_name_callback(field_name, (lat, lng, radius))

        self.accept()

    def show_message(self, title, text, icon):
        """Показывает увеличенное сообщение"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(icon)

        # Увеличиваем шрифт
        font = QFont()
        font.setPointSize(14)  # Увеличили размер шрифта
        msg.setFont(font)

        # Увеличиваем размер окна
        msg.setMinimumSize(600, 300)  # Увеличили минимальные размеры
        msg.resize(600, 300)  # Установили начальный размер

        # Применяем стили для увеличения размера содержимого
        msg.setStyleSheet("""
            QMessageBox {
                min-width: 600px;
                min-height: 300px;
                background-color: white;
            }
            QMessageBox QLabel {
                font-size: 16px;
                min-height: 150px;
                qproperty-alignment: AlignCenter;
            }
            QMessageBox QPushButton {
                font-size: 14px;
                min-width: 120px;
                min-height: 50px;
                padding: 10px;
                background-color: #f0f0f0;
                border: 2px solid #cccccc;
                border-radius: 5px;
            }
            QMessageBox QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)

        msg.exec()

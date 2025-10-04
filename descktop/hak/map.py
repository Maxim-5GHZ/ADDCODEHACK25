import os
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import QUrl, Qt
from bridge.map_bridge import MapBridge

class MapDialog(QDialog):
    def __init__(self, parent=None, coord_callback=None):
        super().__init__(parent)
        self.coord_callback = coord_callback
        self.map_browser = None
        self.setup_ui()

    def setup_ui(self):
        """Создает и настраивает виджет карты в диалоговом окне"""
        try:
            self.setWindowTitle("Выберите точку на карте")
            self.setMinimumSize(800, 600)

            layout = QVBoxLayout(self)

            # Создаем веб-виджет для карты
            self.map_browser = QWebEngineView()
            self.map_browser.setContextMenuPolicy(Qt.DefaultContextMenu)

            # Добавляем обработчики загрузки для отладки
            self.map_browser.loadStarted.connect(lambda: print("Началась загрузка карты..."))
            self.map_browser.loadFinished.connect(self.on_map_loaded)

            # Создаем канал для обмена данными
            self.channel = QWebChannel()
            self.bridge = MapBridge(self.handle_map_click)
            self.channel.registerObject("pyObj", self.bridge)
            self.map_browser.page().setWebChannel(self.channel)

            print("QWebChannel настроен")

            # Загружаем карту
            self.load_basic_map()

            layout.addWidget(self.map_browser)

            # Кнопка закрытия
            close_button = QPushButton("Закрыть карту")
            close_button.clicked.connect(self.close)
            layout.addWidget(close_button)

        except Exception as e:
            print(f"Ошибка в setup_ui: {e}")

    def on_map_loaded(self, success):
        """Обработчик завершения загрузки карты"""
        if success:
            print("Карта успешно загружена")
            # Дополнительная инициализация QWebChannel в JavaScript
            init_script = """
                if (typeof qt !== 'undefined' && qt.webChannelTransport) {
                    new QWebChannel(qt.webChannelTransport, function(channel) {
                        window.pyObj = channel.objects.pyObj;
                        console.log("QWebChannel инициализирован в JavaScript");
                    });
                } else {
                    console.error("QWebChannel не доступен в JavaScript");
                }
            """
            self.map_browser.page().runJavaScript(init_script)
        else:
            print("Ошибка загрузки карты")

    def load_basic_map(self):
        """Загружает базовую карту с улучшенной обработкой QWebChannel"""
        html_content = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Карта</title>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <style>
                #map {
                    height: 100%;
                    width: 100%;
                    position: absolute;
                    top: 0;
                    bottom: 0;
                    left: 0;
                    right: 0;
                }
                body {
                    margin: 0;
                    padding: 0;
                    height: 100vh;
                    overflow: hidden;
                }
                html {
                    height: 100%;
                }
                .loading {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    z-index: 1000;
                    background: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.3);
                }
            </style>
        </head>
        <body>
            <div id="map">
                <div class="loading">Загрузка карты...</div>
            </div>
            <script>
                // Удаляем сообщение о загрузке после инициализации карты
                function removeLoading() {
                    var loading = document.querySelector('.loading');
                    if (loading) {
                        loading.style.display = 'none';
                    }
                }

                // Создаем карту
                var map = L.map('map').setView([55.7558, 37.6173], 10);

                // Основной слой OpenStreetMap
                var osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap contributors',
                    maxZoom: 19
                }).addTo(map);

                // Убираем сообщение о загрузке после успешной загрузки карты
                map.whenReady(removeLoading);

                var marker = null;

                // Инициализация QWebChannel
                function initQWebChannel() {
                    if (typeof QWebChannel !== 'undefined') {
                        new QWebChannel(qt.webChannelTransport, function(channel) {
                            window.pyObj = channel.objects.pyObj;
                            console.log("QWebChannel инициализирован, pyObj доступен");
                        });
                    } else {
                        console.error("QWebChannel не загружен");
                        // Пробуем снова через секунду
                        setTimeout(initQWebChannel, 1000);
                    }
                }

                // Запускаем инициализацию QWebChannel
                initQWebChannel();

                function onMapClick(e) {
                    console.log("Карта кликнута: ", e.latlng);

                    if (window.pyObj) {
                        console.log("Отправляю координаты в Python...");
                        window.pyObj.receiveCoords(e.latlng.lat, e.latlng.lng);
                    } else {
                        console.error("pyObj не доступен. QWebChannel не работает.");
                        alert("Ошибка связи с приложением. Перезагрузите карту.");
                    }

                    // Добавляем маркер
                    if (marker) {
                        map.removeLayer(marker);
                    }
                    marker = L.marker(e.latlng).addTo(map);
                    marker.bindPopup("Координаты: " + e.latlng.lat.toFixed(6) + ", " + e.latlng.lng.toFixed(6)).openPopup();
                }

                map.on('click', onMapClick);
            </script>
        </body>
        </html>
        '''

        # Устанавливаем HTML с базовым URL для корректной работы qrc:///
        self.map_browser.setHtml(html_content, QUrl("qrc:///"))

    def handle_map_click(self, lat, lng):
        """Обрабатывает клик по карте - получает координаты"""
        if self.coord_callback:
            self.coord_callback(lat, lng)
        self.close()

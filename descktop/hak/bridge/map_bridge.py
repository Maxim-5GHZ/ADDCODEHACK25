from PySide6.QtCore import QObject, Slot

class MapBridge(QObject):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @Slot(float, float)
    def receiveCoords(self, lat, lng):
        """Получает координаты из JavaScript и передает в callback"""
        self.callback(lat, lng)

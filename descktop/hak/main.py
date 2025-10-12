import sys
import os
import requests
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from mainwindow import MainWindow

def main():
    # Отключаем предупреждения SSL для самоподписанных сертификатов
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Создаем приложение
    app = QApplication(sys.argv)
    
    # Устанавливаем иконку для всего приложения
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "app_icon.ico")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
    except Exception as e:
        print(f"Не удалось загрузить иконку: {e}")
    
    # Создаем и показываем главное окно
    widget = MainWindow()
    widget.showMaximized()
    
    # Запускаем главный цикл приложения
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
# This Python file uses the following encoding: utf-8
import sys
import os

# Получаем абсолютный путь к текущей директории (где находится main.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Текущая директория: {current_dir}")

# Добавляем текущую директорию в путь Python
sys.path.insert(0, current_dir)

# Теперь импортируем модули
from PySide6.QtWidgets import QApplication

try:
    from widgets.main_window import MainWindow
    print("Модуль widgets успешно импортирован")
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Содержимое текущей директории:")
    for item in os.listdir(current_dir):
        print(f"  {item}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.showMaximized()
    sys.exit(app.exec())

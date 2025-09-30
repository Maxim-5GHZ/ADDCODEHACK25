# main.py
import controller
import socket
import logging
import time

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_local_ip():
    """Получает локальный IP-адрес компьютера"""
    try:
        logger.info("Получение локального IP-адреса...")
        # Создаем временное соединение чтобы определить IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(("8.8.8.8", 80))  # Подключаемся к Google DNS
        local_ip = s.getsockname()[0]
        s.close()
        logger.info(f"Локальный IP-адрес: {local_ip}")
        return local_ip
    except Exception as e:
        logger.error(f"Ошибка при получении локального IP: {e}")
        # Пробуем альтернативный способ
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            logger.info(f"Локальный IP-адрес (альтернативный метод): {local_ip}")
            return local_ip
        except Exception as e2:
            logger.error(f"Альтернативный метод также не сработал: {e2}")
            return "127.0.0.1"


def check_port_availability(port=8000):
    """Проверяет доступность порта"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return True
    except socket.error:
        return False


if __name__ == "__main__":
    logger.info("Запуск приложения...")

    # Проверяем доступность порта bde756b
    if not check_port_availability(8000):
        logger.error("Порт 8000 уже занят!")
        print("ОШИБКА: Порт 8000 уже занят другим процессом")
        print("Закройте другие приложения, использующие порт 8000, и попробуйте снова")
        exit(1)

    local_ip = get_local_ip()
    print(f"Сервер будет доступен по адресам:")
    print(f"Локально: http://localhost:8000")
    print(f"В сети: http://{local_ip}:8000")
    print("Для остановки сервера нажмите Ctrl+C")

    try:
        server = controller.controller()
        server.run()
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске сервера: {e}")
        print(f"Критическая ошибка: {e}")
        time.sleep(5)  # Даем время прочитать сообщение об ошибке
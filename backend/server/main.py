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




if __name__ == "__main__":
    logger.info("Запуск приложения...")

    # Проверяем доступность порта bde756b


    local_ip = get_local_ip()
    print(f"Сервер будет доступен по адресам:")
    print(f"Локально: http://localhost:8000")
    print(f"В сети: http://{local_ip}:8000")
    print("Для остановки сервера нажмите Ctrl+C")

    try:
        server = controller.controller('8000')
        server.run()
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске сервера: {e}")
        print(f"Критическая ошибка: {e}")
        time.sleep(5)  # Даем время прочитать сообщение об ошибке
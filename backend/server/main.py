import controller
import logging
import time


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scr/app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("Запуск приложения...")
    try:
        server = controller.controller(port="8000", use_https=False,token_use=0)
        server.run()
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске сервера: {e}")
        print(f"Критическая ошибка: {e}")
        time.sleep(5)  # Даем время прочитать сообщение об ошибке
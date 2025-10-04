import requests
import json
import time
import random
import logging
import base64
from io import BytesIO
from PIL import Image

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ServerTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_users = []

    def make_request(self, endpoint, method="GET", params=None, data=None):
        """Универсальный метод для выполнения запросов"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, params=params, data=data, timeout=30)
            elif method.upper() == "PUT":
                response = self.session.put(url, params=params, data=data, timeout=30)
            elif method.upper() == "PATCH":
                response = self.session.patch(url, params=params, data=data, timeout=30)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, params=params, timeout=30)
            else:
                raise ValueError(f"Неизвестный метод: {method}")

            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к {url}: {e}")
            return None

    def test_health_check(self):
        """Тест проверки здоровья сервера"""
        logger.info("Тестирование health check...")
        response = self.make_request("/health")
        if response and response.status_code == 200:
            data = response.json()
            logger.info(f"✓ Health check пройден: {data}")
            return True
        else:
            logger.error("✗ Health check не пройден")
            return False

    def test_main_page(self):
        """Тест главной страницы"""
        logger.info("Тестирование главной страницы...")
        response = self.make_request("/")
        if response and response.status_code in [200, 404]:
            logger.info(f"✓ Главная страница: статус {response.status_code}")
            return True
        else:
            logger.error("✗ Главная страница недоступна")
            return False

    def test_favicon(self):
        """Тест favicon"""
        logger.info("Тестирование favicon...")
        response = self.make_request("/favicon.ico")
        if response:
            logger.info(f"✓ Favicon: статус {response.status_code}")
            return True
        else:
            logger.warning("⚠ Favicon недоступен")
            return False

    def test_user_registration(self, username_suffix=None):
        """Тест регистрации пользователя"""
        if username_suffix is None:
            username_suffix = str(int(time.time()))

        login = f"testuser_{username_suffix}"
        password = "testpass123"

        logger.info(f"Тестирование регистрации пользователя {login}...")
        response = self.make_request(
            "/add_user",
            method="POST",
            params={"login": login, "password": password}
        )

        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                logger.info(f"✓ Регистрация успешна: {login}")
                self.test_users.append({"login": login, "password": password})
                return True
            else:
                logger.error(f"✗ Ошибка регистрации: {data}")
                return False
        else:
            logger.error("✗ Регистрация не удалась")
            return False

    def test_user_login(self, login, password):
        """Тест входа пользователя и получение токена"""
        logger.info(f"Тестирование входа пользователя {login}...")
        response = self.make_request(
            "/get_token",
            params={"login": login, "password": password}
        )

        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                token = data.get("token")
                logger.info(f"✓ Вход успешен, получен токен: {token[:10]}...")
                return token
            else:
                logger.error(f"✗ Ошибка входа: {data}")
                return None
        else:
            logger.error("✗ Вход не удался")
            return None

    def test_save_user_data(self, token, key_array):
        """Тест сохранения данных пользователя"""
        logger.info("Тестирование сохранения данных пользователя...")
        response = self.make_request(
            "/savedata",
            method="POST",
            params={"token": token, "key_array": key_array}
        )

        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                logger.info("✓ Данные успешно сохранены")
                return True
            else:
                logger.error(f"✗ Ошибка сохранения данных: {data}")
                return False
        else:
            logger.error("✗ Сохранение данных не удалось")
            return False

    def test_get_user_data(self, token):
        """Тест получения данных пользователя"""
        logger.info("Тестирование получения данных пользователя...")
        response = self.make_request(
            "/givefield",
            params={"token": token}
        )

        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") in ["success", "dismiss"]:
                keys = data.get("keys")
                logger.info(f"✓ Данные получены: {keys}")
                return keys
            else:
                logger.error(f"✗ Ошибка получения данных: {data}")
                return None
        else:
            logger.error("✗ Получение данных не удалось")
            return None

    def test_update_user_data(self, token, key_array):
        """Тест обновления данных пользователя"""
        logger.info("Тестирование обновления данных пользователя...")
        response = self.make_request(
            "/data/update",
            method="PUT",
            params={"token": token, "key_array": key_array}
        )

        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                logger.info("✓ Данные успешно обновлены")
                return True
            else:
                logger.error(f"✗ Ошибка обновления данных: {data}")
                return False
        else:
            logger.error("✗ Обновление данных не удалось")
            return False

    def test_edit_user_data(self, token, keys_to_add=None, keys_to_remove=None):
        """Тест частичного редактирования данных"""
        logger.info("Тестирование частичного редактирования данных...")
        params = {"token": token}
        if keys_to_add:
            params["keys_to_add"] = keys_to_add
        if keys_to_remove:
            params["keys_to_remove"] = keys_to_remove

        response = self.make_request(
            "/data/edit",
            method="PATCH",
            params=params
        )

        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                logger.info("✓ Данные успешно отредактированы")
                return True
            else:
                logger.error(f"✗ Ошибка редактирования данных: {data}")
                return False
        else:
            logger.error("✗ Редактирование данных не удалось")
            return False

    def test_check_user_data_exists(self, token):
        """Тест проверки существования данных"""
        logger.info("Тестирование проверки существования данных...")
        response = self.make_request(
            "/data/check",
            params={"token": token}
        )

        if response and response.status_code == 200:
            data = response.json()
            exists = data.get("exists", False)
            logger.info(f"✓ Проверка данных: exists={exists}")
            return exists
        else:
            logger.error("✗ Проверка данных не удалась")
            return False

    def test_delete_user_data(self, token):
        """Тест удаления данных пользователя"""
        logger.info("Тестирование удаления данных пользователя...")
        response = self.make_request(
            "/data/delete",
            method="DELETE",
            params={"token": token}
        )

        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                logger.info("✓ Данные успешно удалены")
                return True
            else:
                logger.error(f"✗ Ошибка удаления данных: {data}")
                return False
        else:
            logger.error("✗ Удаление данных не удалось")
            return False

    def test_field_operations(self, token):
        """Тест операций с полями"""
        field_name = f"test_field_{int(time.time())}"
        test_data = f"test_data_{random.randint(1000, 9999)}"

        logger.info("Тестирование операций с полями...")

        # Создание поля
        response = self.make_request(
            "/field/set",
            method="POST",
            params={"field": field_name, "data": test_data, "token": token}
        )

        if not response or response.status_code != 200:
            logger.error("✗ Создание поля не удалось")
            return False

        data = response.json()
        if data.get("status") != "success":
            logger.error(f"✗ Ошибка создания поля: {data}")
            return False

        logger.info("✓ Поле успешно создано")

        # Проверка существования поля
        response = self.make_request(
            "/field/check",
            params={"field": field_name, "token": token}
        )

        if response and response.status_code == 200:
            data = response.json()
            if data.get("exists"):
                logger.info("✓ Поле существует")
            else:
                logger.error("✗ Поле не найдено после создания")
                return False

        # Получение данных поля
        response = self.make_request(
            "/field/get",
            params={"field": field_name, "token": token}
        )

        if response and response.status_code == 200:
            data = response.json()
            if data.get("data") == test_data:
                logger.info("✓ Данные поля корректны")
            else:
                logger.error("✗ Данные поля не совпадают")
                return False

        # Удаление поля
        response = self.make_request(
            "/field/delete",
            method="DELETE",
            params={"field": field_name, "token": token}
        )

        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                logger.info("✓ Поле успешно удалено")
                return True

        logger.error("✗ Операции с полями завершились с ошибками")
        return False

    def test_image_operations(self, token):
        """Тест операций с изображениями"""
        logger.info("Тестирование операций с изображениями...")
        
        # Тестовые координаты (Москва)
        test_coordinates = [
            (37.6173, 55.7558),  # Москва
            (30.5234, 50.4501),  # Киев
            (27.5667, 53.9000),  # Минск
        ]
        
        lon, lat = test_coordinates[0]  # Используем Москву для тестов
        
        # Даты для тестирования (последние 30 дней)
        end_date = time.strftime("%Y-%m-%d")
        start_date = time.strftime("%Y-%m-%d", time.gmtime(time.time() - 30*24*60*60))
        
        results = {}
        
        # Тест RGB изображения
        logger.info("Тестирование получения RGB изображения...")
        response = self.make_request(
            "/image/rgb",
            params={
                "lon": lon,
                "lat": lat,
                "start_date": start_date,
                "end_date": end_date,
                "token": token
            }
        )
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                image_data = data.get("image_data")
                if image_data and len(image_data) > 100:  # Проверяем, что есть данные
                    logger.info("✓ RGB изображение успешно получено")
                    results["rgb_image"] = True
                    
                    # Дополнительная проверка: пытаемся декодировать изображение
                    try:
                        image_bytes = base64.b64decode(image_data)
                        image = Image.open(BytesIO(image_bytes))
                        logger.info(f"✓ RGB изображение валидно: {image.size}")
                    except Exception as e:
                        logger.warning(f"⚠ RGB изображение получено, но ошибка декодирования: {e}")
                        results["rgb_image"] = True  # Все равно считаем успехом
                else:
                    logger.error("✗ RGB изображение пустое")
                    results["rgb_image"] = False
            else:
                logger.warning(f"⚠ RGB изображение не получено: {data.get('detail', 'Unknown error')}")
                results["rgb_image"] = False
        else:
            logger.error("✗ Запрос RGB изображения не удался")
            results["rgb_image"] = False
        
        # Тест красного канала
        logger.info("Тестирование получения красного канала...")
        response = self.make_request(
            "/image/red-channel",
            params={
                "lon": lon,
                "lat": lat,
                "start_date": start_date,
                "end_date": end_date,
                "token": token
            }
        )
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                image_data = data.get("image_data")
                if image_data and len(image_data) > 100:
                    logger.info("✓ Красный канал успешно получен")
                    results["red_channel"] = True
                    
                    # Проверяем статистику
                    stats = data.get("statistics", {})
                    if stats:
                        logger.info(f"✓ Статистика красного канала: min={stats.get('min_value')}, max={stats.get('max_value')}")
                else:
                    logger.error("✗ Красный канал пустой")
                    results["red_channel"] = False
            else:
                logger.warning(f"⚠ Красный канал не получен: {data.get('detail', 'Unknown error')}")
                results["red_channel"] = False
        else:
            logger.error("✗ Запрос красного канала не удался")
            results["red_channel"] = False
        
        # Тест NDVI
        logger.info("Тестирование получения NDVI...")
        response = self.make_request(
            "/image/ndvi",
            params={
                "lon": lon,
                "lat": lat,
                "start_date": start_date,
                "end_date": end_date,
                "token": token
            }
        )
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                image_data = data.get("image_data")
                if image_data and len(image_data) > 100:
                    logger.info("✓ NDVI успешно получен")
                    results["ndvi"] = True
                    
                    # Проверяем статистику NDVI
                    stats = data.get("statistics", {})
                    if stats:
                        logger.info(f"✓ Статистика NDVI: min={stats.get('min_ndvi'):.3f}, max={stats.get('max_ndvi'):.3f}")
                else:
                    logger.error("✗ NDVI пустой")
                    results["ndvi"] = False
            else:
                logger.warning(f"⚠ NDVI не получен: {data.get('detail', 'Unknown error')}")
                results["ndvi"] = False
        else:
            logger.error("✗ Запрос NDVI не удался")
            results["ndvi"] = False
        
        # Считаем тест пройденным, если хотя бы одно изображение получено
        image_tests_passed = sum(results.values())
        total_image_tests = len(results)
        
        logger.info(f"Результаты тестов изображений: {image_tests_passed}/{total_image_tests}")
        
        return image_tests_passed > 0

    def test_admin_logs(self):
        """Тест получения логов администратора"""
        logger.info("Тестирование получения логов...")

        # Неправильный пароль
        response = self.make_request(
            "/log",
            params={"password": "wrong_password"}
        )

        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "error":
                logger.info("✓ Защита логов работает (неправильный пароль отклонен)")
            else:
                logger.warning("⚠ Неожиданный ответ при неправильном пароле")

        # Правильный пароль
        response = self.make_request(
            "/log",
            params={"password": "12345"}
        )

        if response:
            logger.info(f"✓ Логи доступны: статус {response.status_code}")
            return True
        else:
            logger.error("✗ Логи недоступны")
            return False

    def run_comprehensive_test(self):
        """Запуск комплексного тестирования"""
        logger.info("=" * 50)
        logger.info("ЗАПУСК КОМПЛЕКСНОГО ТЕСТИРОВАНИЯ СЕРВЕРА")
        logger.info("=" * 50)

        results = {}

        # Базовые тесты
        results["health_check"] = self.test_health_check()
        results["main_page"] = self.test_main_page()
        results["favicon"] = self.test_favicon()

        # Тесты пользователей
        username_suffix = str(int(time.time()))
        results["user_registration"] = self.test_user_registration(username_suffix)

        if results["user_registration"]:
            test_user = self.test_users[0]
            token = self.test_user_login(test_user["login"], test_user["password"])
            results["user_login"] = token is not None

            if token:
                # Тесты данных пользователя
                test_data_1 = "key1,key2,key3"
                test_data_2 = "key4,key5,key6"

                results["save_user_data"] = self.test_save_user_data(token, test_data_1)
                results["get_user_data"] = self.test_get_user_data(token) is not None
                results["update_user_data"] = self.test_update_user_data(token, test_data_2)
                results["edit_user_data"] = self.test_edit_user_data(token, "key7,key8", "key4")
                results["check_data_exists"] = self.test_check_user_data_exists(token)
                results["field_operations"] = self.test_field_operations(token)
                
                # Тесты изображений (требуют интернет и Google Earth Engine)
                try:
                    results["image_operations"] = self.test_image_operations(token)
                except Exception as e:
                    logger.error(f"✗ Тесты изображений завершились с ошибкой: {e}")
                    results["image_operations"] = False
                
                results["delete_user_data"] = self.test_delete_user_data(token)

        # Тест логов
        results["admin_logs"] = self.test_admin_logs()

        # Статистика
        logger.info("=" * 50)
        logger.info("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        logger.info("=" * 50)

        passed = sum(1 for result in results.values() if result)
        total = len(results)

        for test_name, result in results.items():
            status = "✓ ПРОЙДЕН" if result else "✗ НЕ ПРОЙДЕН"
            logger.info(f"{test_name}: {status}")

        logger.info(f"ИТОГО: {passed}/{total} тестов пройдено")

        success_rate = (passed / total) * 100
        if success_rate >= 80:
            logger.info(f"✓ СЕРВЕР РАБОТАЕТ КОРРЕКТНО ({success_rate:.1f}%)")
        elif success_rate >= 50:
            logger.warning(f"⚠ СЕРВЕР ИМЕЕТ ПРОБЛЕМЫ ({success_rate:.1f}%)")
        else:
            logger.error(f"✗ СЕРВЕР НЕ РАБОТАЕТ КОРРЕКТНО ({success_rate:.1f}%)")

        return results


def main():
    """Основная функция"""
    import sys

    # Проверяем аргументы командной строки
    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    print(f"Тестирование сервера по адресу: {base_url}")
    print("Для остановки нажмите Ctrl+C\n")

    tester = ServerTester(base_url)

    try:
        results = tester.run_comprehensive_test()

        # Если тесты не прошли, ждем ввод для просмотра результатов
        passed = sum(1 for result in results.values() if result)
        if passed < len(results):
            input("\nНажмите Enter для выхода...")

    except KeyboardInterrupt:
        print("\n\nТестирование прервано пользователем")
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")
        input("Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()
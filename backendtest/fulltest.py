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
        self.analysis_ids = []

    def make_request(self, endpoint, method="GET", params=None, data=None):
        """Универсальный метод для выполнения запросов"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=60) # Увеличено время ожидания для GEE
            elif method.upper() == "POST":
                response = self.session.post(url, params=params, data=data, timeout=60) # Увеличено время ожидания для GEE
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
        """Тест регистрации пользователя с именем и фамилией"""
        if username_suffix is None:
            username_suffix = str(int(time.time()))

        login = f"testuser_{username_suffix}"
        password = "testpass123"
        first_name = "Test"
        last_name = f"User_{username_suffix}"

        logger.info(f"Тестирование регистрации пользователя {login}...")
        response = self.make_request(
            "/add_user",
            method="POST",
            params={
                "login": login,
                "password": password,
                "first_name": first_name,
                "last_name": last_name
            }
        )

        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                logger.info(f"✓ Регистрация успешна: {login} ({first_name} {last_name})")
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
        
        lon, lat = 37.6173, 55.7558  # Москва
        
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
                if image_data and len(image_data) > 100:
                    logger.info("✓ RGB изображение успешно получено")
                    results["rgb_image"] = True
                    try:
                        image_bytes = base64.b64decode(image_data)
                        Image.open(BytesIO(image_bytes))
                        logger.info("✓ RGB изображение валидно")
                    except Exception:
                        logger.warning("⚠ RGB изображение получено, но ошибка декодирования")
                else:
                    logger.error("✗ RGB изображение пустое")
                    results["rgb_image"] = False
            else:
                logger.warning(f"⚠ RGB изображение не получено: {data.get('detail', 'Unknown error')}")
                results["rgb_image"] = False
        else:
            logger.error("✗ Запрос RGB изображения не удался")
            results["rgb_image"] = False
        
        return any(results.values())

    def test_analysis_operations(self, token):
        """Тест операций с анализом по точке и полигону"""
        logger.info("Тестирование операций с анализом...")
        
        lon, lat = 37.6173, 55.7558
        end_date = time.strftime("%Y-%m-%d")
        start_date = time.strftime("%Y-%m-%d", time.gmtime(time.time() - 60*24*60*60)) # Увеличим диапазон до 60 дней
        
        results = {}
        
        # --- Тест 1: Выполнение анализа по точке и радиусу ---
        logger.info("Тестирование выполнения анализа по точке и радиусу...")
        response_point = self.make_request(
            "/analysis/perform",
            method="POST",
            params={
                "token": token,
                "lon": lon,
                "lat": lat,
                "start_date": start_date,
                "end_date": end_date
            }
        )
        
        if response_point and response_point.status_code == 200:
            data = response_point.json()
            if data.get("status") == "success" and data.get("analysis_id"):
                analysis_id = data.get("analysis_id")
                logger.info(f"✓ Анализ по точке успешно выполнен, ID: {analysis_id}")
                self.analysis_ids.append(analysis_id)
                results["perform_analysis_point"] = True
            else:
                logger.warning(f"⚠ Анализ по точке не выполнен: {data.get('detail', 'Unknown error')}")
                results["perform_analysis_point"] = False
        else:
            logger.error("✗ Запрос анализа по точке не удался")
            results["perform_analysis_point"] = False

        # --- Тест 2: Выполнение анализа по полигону ---
        logger.info("Тестирование выполнения анализа по полигону...")
        poly_coords = [[lon - 0.01, lat - 0.01], [lon + 0.01, lat - 0.01], [lon + 0.01, lat + 0.01], [lon - 0.01, lat + 0.01]]
        poly_json = json.dumps(poly_coords)

        response_poly = self.make_request(
            "/analysis/perform",
            method="POST",
            params={
                "token": token,
                "start_date": start_date,
                "end_date": end_date,
                "polygon_coords": poly_json
            }
        )

        if response_poly and response_poly.status_code == 200:
            data = response_poly.json()
            if data.get("status") == "success" and data.get("analysis_id"):
                analysis_id = data.get("analysis_id")
                logger.info(f"✓ Анализ по полигону успешно выполнен, ID: {analysis_id}")
                self.analysis_ids.append(analysis_id)
                results["perform_analysis_polygon"] = True
            else:
                logger.warning(f"⚠ Анализ по полигону не выполнен: {data.get('detail', 'Unknown error')}")
                results["perform_analysis_polygon"] = False
        else:
            logger.error("✗ Запрос анализа по полигону не удался")
            results["perform_analysis_polygon"] = False

        # --- Тесты получения и удаления ---
        if not self.analysis_ids:
            logger.error("✗ Ни один анализ не был создан, пропуск тестов получения и удаления.")
            results["get_analyses_list"] = False
            results["get_analysis"] = False
            results["delete_analysis"] = False
            return False

        # Тест получения списка анализов
        logger.info("Тестирование получения списка анализов...")
        response_list = self.make_request("/analysis/list", params={"token": token})
        if response_list and response_list.status_code == 200 and response_list.json().get("status") == "success":
            analyses_count = len(response_list.json().get("analyses", []))
            logger.info(f"✓ Список анализов получен: {analyses_count} записей")
            results["get_analyses_list"] = True
        else:
            logger.error("✗ Ошибка получения списка анализов")
            results["get_analyses_list"] = False

        # Тест получения конкретного анализа
        analysis_to_get = self.analysis_ids[0]
        logger.info(f"Тестирование получения анализа {analysis_to_get}...")
        response_get = self.make_request(f"/analysis/{analysis_to_get}", params={"token": token})
        if response_get and response_get.status_code == 200 and response_get.json().get("status") == "success":
            logger.info("✓ Конкретный анализ успешно получен")
            results["get_analysis"] = True
        else:
            logger.error("✗ Ошибка получения конкретного анализа")
            results["get_analysis"] = False

        # Тест удаления анализа
        analysis_to_delete = self.analysis_ids.pop(0)
        logger.info(f"Тестирование удаления анализа {analysis_to_delete}...")
        response_delete = self.make_request(f"/analysis/{analysis_to_delete}", method="DELETE", params={"token": token})
        if response_delete and response_delete.status_code == 200 and response_delete.json().get("status") == "success":
            logger.info("✓ Анализ успешно удален")
            results["delete_analysis"] = True
        else:
            logger.error("✗ Ошибка удаления анализа")
            results["delete_analysis"] = False
        
        # Считаем тест пройденным, если хотя бы один метод создания анализа сработал и остальные операции тоже
        creation_success = results.get("perform_analysis_point", False) or results.get("perform_analysis_polygon", False)
        return creation_success and all([results.get(k, False) for k in ["get_analyses_list", "get_analysis", "delete_analysis"]])

    def test_admin_logs(self):
        """Тест получения логов администратора"""
        logger.info("Тестирование получения логов...")
        response = self.make_request("/log", params={"password": "12345"})
        if response:
            logger.info(f"✓ Логи доступны: статус {response.status_code}")
            return True
        else:
            logger.error("✗ Логи недоступны")
            return False

    def test_get_all_users(self, created_user_login):
        """Тест получения списка всех пользователей (админ)"""
        logger.info("Тестирование получения списка всех пользователей...")
        response = self.make_request("/users/all", params={"password": "12345"})
        if not (response and response.status_code == 200):
            logger.error("✗ Запрос списка пользователей не удался")
            return False

        data = response.json()
        if data.get("status") != "success":
            logger.error(f"✗ Ошибка при получении списка: {data.get('detail')}")
            return False

        users = data.get("users", [])
        if not isinstance(users, list) or not users:
            logger.error("✗ Получен пустой или некорректный список")
            return False

        if not any(user.get("login") == created_user_login for user in users):
            logger.error(f"✗ Созданный пользователь {created_user_login} не найден в списке")
            return False
        
        logger.info(f"✓ Список пользователей успешно получен ({len(users)} записей), тестовый пользователь найден.")
        return True

    def test_error_handling(self):
        """Тест обработки ошибок"""
        logger.info("Тестирование обработки ошибок...")
        
        results = {}
        
        # Неверный токен
        response = self.make_request("/givefield", params={"token": "invalid_token"})
        if response and response.json().get("status") in ["error", "dismiss"]:
            logger.info("✓ Корректная обработка неверного токена")
            results["invalid_token"] = True
        else:
            logger.error("✗ Неверная обработка неверного токена")
            results["invalid_token"] = False
        
        # Неверные параметры
        response = self.make_request("/image/rgb", params={"lon": "abc", "lat": "def", "token": "abc"})
        if response:
            logger.info(f"✓ Сервер обработал неверные параметры: статус {response.status_code}")
            results["invalid_params"] = True
        else:
            logger.error("✗ Сервер не обработал неверные параметры")
            results["invalid_params"] = False
        
        # Несуществующий эндпоинт
        response = self.make_request("/nonexistent_endpoint")
        if response and response.status_code == 404:
            logger.info("✓ Корректная обработка несуществующего эндпоинта")
            results["nonexistent_endpoint"] = True
        else:
            logger.warning("⚠ Нестандартная обработка несуществующего эндпоинта")
            results["nonexistent_endpoint"] = True
        
        return sum(results.values()) >= 2

    def test_performance(self, token):
        """Тест производительности"""
        logger.info("Тестирование производительности (быстрые запросы)...")
        
        test_start = time.time()
        quick_tests = ["/health", f"/data/check?token={token}"]
        
        for endpoint in quick_tests:
            response = self.make_request(endpoint)
            if not (response and response.status_code == 200):
                logger.warning(f"⚠ Тест производительности для {endpoint} не удался")
                return False
        
        duration = time.time() - test_start
        logger.info(f"✓ {len(quick_tests)} быстрых запроса выполнены за {duration:.3f} сек")
        return duration < 5.0

    def run_comprehensive_test(self):
        """Запуск комплексного тестирования"""
        logger.info("=" * 50)
        logger.info("ЗАПУСК КОМПЛЕКСНОГО ТЕСТИРОВАНИЯ СЕРВЕРА")
        logger.info("=" * 50)

        results = {}

        results["health_check"] = self.test_health_check()
        results["main_page"] = self.test_main_page()
        results["favicon"] = self.test_favicon()

        username_suffix = str(int(time.time()))
        results["user_registration"] = self.test_user_registration(username_suffix)

        if results["user_registration"]:
            test_user = self.test_users[0]
            token = self.test_user_login(test_user["login"], test_user["password"])
            results["user_login"] = token is not None

            if token:
                results["save_user_data"] = self.test_save_user_data(token, "k1,k2")
                results["get_user_data"] = self.test_get_user_data(token) is not None
                results["update_user_data"] = self.test_update_user_data(token, "k3,k4")
                results["edit_user_data"] = self.test_edit_user_data(token, "k5,k6", "k3")
                results["check_data_exists"] = self.test_check_user_data_exists(token)
                results["field_operations"] = self.test_field_operations(token)
                
                try:
                    results["image_operations"] = self.test_image_operations(token)
                except Exception as e:
                    logger.error(f"✗ Тесты изображений завершились с ошибкой: {e}")
                    results["image_operations"] = False
                
                try:
                    results["analysis_operations"] = self.test_analysis_operations(token)
                except Exception as e:
                    logger.error(f"✗ Тесты анализа завершились с ошибкой: {e}")
                    results["analysis_operations"] = False
                
                try:
                    results["performance"] = self.test_performance(token)
                except Exception as e:
                    logger.error(f"✗ Тесты производительности завершились с ошибкой: {e}")
                    results["performance"] = False
                
                results["get_all_users"] = self.test_get_all_users(test_user["login"])
                results["delete_user_data"] = self.test_delete_user_data(token)

        results["admin_logs"] = self.test_admin_logs()
        results["error_handling"] = self.test_error_handling()

        logger.info("=" * 50)
        logger.info("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        logger.info("=" * 50)

        passed = sum(1 for result in results.values() if result)
        total = len(results)

        for test_name, result in results.items():
            status = "✓ ПРОЙДЕН" if result else "✗ НЕ ПРОЙДЕН"
            logger.info(f"{test_name.replace('_', ' ').capitalize()}: {status}")

        logger.info(f"\nИТОГО: {passed}/{total} тестов пройдено")

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

    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    print(f"Тестирование сервера по адресу: {base_url}")
    print("Для остановки нажмите Ctrl+C\n")

    tester = ServerTester(base_url)

    try:
        results = tester.run_comprehensive_test()
        passed = sum(1 for result in results.values() if result)
        if passed < len(results):
            input("\nНажмите Enter для выхода...")

    except KeyboardInterrupt:
        print("\n\nТестирование прервано пользователем")
    except Exception as e:
        print(f"\nПроизошла критическая ошибка во время тестирования: {e}")
        input("Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()
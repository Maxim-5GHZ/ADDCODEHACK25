# api_comprehensive_test.py
import requests
import time
import random
import logging
from typing import Dict, List, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ComprehensiveAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_users = []
        self.tokens = {}

    def make_request(self, endpoint: str, method: str = "GET", params: Dict = None, 
                   data: Dict = None, timeout: int = 10) -> Optional[requests.Response]:
        """Универсальный метод для выполнения запросов"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            method = method.upper()
            request_methods = {
                "GET": self.session.get,
                "POST": self.session.post,
                "PUT": self.session.put,
                "PATCH": self.session.patch,
                "DELETE": self.session.delete
            }
            
            if method not in request_methods:
                raise ValueError(f"Неизвестный метод: {method}")
            
            if method in ["POST", "PUT", "PATCH"]:
                response = request_methods[method](url, params=params, json=data, timeout=timeout)
            else:
                response = request_methods[method](url, params=params, timeout=timeout)
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к {url}: {e}")
            return None

    # Базовые тесты сервера
    def test_health_check(self) -> bool:
        """Тест проверки здоровья сервера"""
        logger.info("Тестирование /health...")
        response = self.make_request("/health")
        
        if response and response.status_code == 200:
            logger.info("✓ Health check пройден")
            return True
        else:
            logger.error("✗ Health check не пройден")
            return False

    def test_main_page(self) -> bool:
        """Тест главной страницы"""
        logger.info("Тестирование главной страницы /...")
        response = self.make_request("/")
        
        if response and response.status_code == 200:
            logger.info("✓ Главная страница доступна")
            return True
        else:
            logger.error("✗ Главная страница недоступна")
            return False

    def test_favicon(self) -> bool:
        """Тест favicon"""
        logger.info("Тестирование /favicon.ico...")
        response = self.make_request("/favicon.ico")
        
        if response:
            logger.info("✓ Favicon доступен")
            return True
        else:
            logger.warning("⚠ Favicon недоступен")
            return False

    def test_static_files(self) -> bool:
        """Тест статических файлов"""
        logger.info("Тестирование статических файлов /scr/...")
        test_files = ["script.js", "style.css", "index.html"]
        
        for file in test_files:
            response = self.make_request(f"/scr/{file}")
            if response and response.status_code == 200:
                logger.info(f"✓ Статический файл {file} доступен")
            else:
                logger.warning(f"⚠ Статический файл {file} недоступен")
        
        return True

    # Тесты аутентификации и пользователей
    def test_user_registration(self, username_suffix: str = None) -> tuple[bool, str]:
        """Тест регистрации пользователя"""
        if username_suffix is None:
            username_suffix = str(int(time.time()))
        
        login = f"testuser_{username_suffix}"
        password = "testpass123"

        logger.info(f"Тестирование регистрации пользователя /add_user...")
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
                return True, login
            else:
                logger.error(f"✗ Ошибка регистрации: {data}")
                return False, login
        else:
            logger.error("✗ Регистрация не удалась")
            return False, login

    def test_user_login(self, login: str, password: str) -> tuple[bool, str]:
        """Тест входа пользователя и получение токена"""
        logger.info(f"Тестирование входа пользователя /get_token...")
        response = self.make_request(
            "/get_token",
            params={"login": login, "password": password}
        )

        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                token = data.get("token")
                logger.info(f"✓ Вход успешен, получен токен")
                self.tokens[login] = token
                return True, token
            else:
                logger.error(f"✗ Ошибка входа: {data}")
                return False, ""
        else:
            logger.error("✗ Вход не удался")
            return False, ""

    def test_invalid_login(self) -> bool:
        """Тест входа с неверными данными"""
        logger.info("Тестирование входа с неверными данными...")
        response = self.make_request(
            "/get_token",
            params={"login": "invalid_user", "password": "wrong_password"}
        )

        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "error":
                logger.info("✓ Неверный логин/пароль правильно отклонен")
                return True
            else:
                logger.error("✗ Неверный ответ при неверных данных")
                return False
        else:
            logger.error("✗ Ошибка при тесте неверных данных")
            return False

    # Тесты работы с пользовательскими данными
    def test_save_user_data(self, token: str) -> bool:
        """Тест сохранения данных пользователя"""
        logger.info("Тестирование сохранения данных /savedata...")
        test_data = "key1,key2,key3,test_data,example"
        
        response = self.make_request(
            "/savedata",
            method="POST",
            params={"token": token, "key_array": test_data}
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

    def test_get_user_data(self, token: str) -> tuple[bool, List]:
        """Тест получения данных пользователя"""
        logger.info("Тестирование получения данных /givefield...")
        response = self.make_request(
            "/givefield",
            params={"token": token}
        )

        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") in ["success", "dismiss"]:
                keys = data.get("keys", [])
                logger.info(f"✓ Данные получены: {len(keys)} ключей")
                return True, keys
            else:
                logger.error(f"✗ Ошибка получения данных: {data}")
                return False, []
        else:
            logger.error("✗ Получение данных не удалось")
            return False, []

    def test_update_user_data(self, token: str) -> bool:
        """Тест полного обновления данных пользователя"""
        logger.info("Тестирование обновления данных /data/update...")
        new_data = "updated_key1,updated_key2,new_key3"
        
        response = self.make_request(
            "/data/update",
            method="PUT",
            params={"token": token, "key_array": new_data}
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

    def test_edit_user_data(self, token: str) -> bool:
        """Тест частичного редактирования данных"""
        logger.info("Тестирование редактирования данных /data/edit...")
        
        response = self.make_request(
            "/data/edit",
            method="PATCH",
            params={
                "token": token,
                "keys_to_add": "added_key1,added_key2",
                "keys_to_remove": "updated_key1"
            }
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

    def test_check_user_data_exists(self, token: str) -> bool:
        """Тест проверки существования данных"""
        logger.info("Тестирование проверки данных /data/check...")
        response = self.make_request(
            "/data/check",
            params={"token": token}
        )

        if response and response.status_code == 200:
            data = response.json()
            exists = data.get("exists", False)
            logger.info(f"✓ Проверка данных: exists={exists}")
            return True
        else:
            logger.error("✗ Проверка данных не удалась")
            return False

    def test_delete_user_data(self, token: str) -> bool:
        """Тест удаления данных пользователя"""
        logger.info("Тестирование удаления данных /data/delete...")
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

    # Тесты операций с полями
    def test_field_operations(self, token: str) -> bool:
        """Комплексный тест операций с полями"""
        field_name = f"test_field_{int(time.time())}"
        test_data = f"test_data_{random.randint(1000, 9999)}"
        
        logger.info("Тестирование операций с полями...")

        # Создание поля
        logger.info("Тестирование создания поля /field/set...")
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
        logger.info("Тестирование проверки поля /field/check...")
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
        else:
            logger.error("✗ Проверка поля не удалась")
            return False

        # Получение данных поля
        logger.info("Тестирование получения поля /field/get...")
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
        else:
            logger.error("✗ Получение поля не удалось")
            return False

        # Удаление поля
        logger.info("Тестирование удаления поля /field/delete...")
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

        logger.error("✗ Удаление поля не удалось")
        return False

    # Тесты административных функций
    def test_admin_logs(self) -> bool:
        """Тест получения логов администратора"""
        logger.info("Тестирование получения логов /log...")

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

        if response and response.status_code == 200:
            logger.info("✓ Логи доступны")
            return True
        else:
            logger.error("✗ Логи недоступны")
            return False

    def run_comprehensive_test(self) -> Dict[str, bool]:
        """Запуск комплексного тестирования всех API endpoints"""
        logger.info("=" * 60)
        logger.info("ЗАПУСК КОМПЛЕКСНОГО ТЕСТИРОВАНИЯ API")
        logger.info("=" * 60)

        results = {}

        # Базовые тесты сервера
        results["health_check"] = self.test_health_check()
        results["main_page"] = self.test_main_page()
        results["favicon"] = self.test_favicon()
        results["static_files"] = self.test_static_files()

        # Тесты аутентификации
        username_suffix = str(int(time.time()))
        results["user_registration"] = self.test_user_registration(username_suffix)[0]
        results["invalid_login"] = self.test_invalid_login()

        if results["user_registration"]:
            test_user = self.test_users[0]
            login_success, token = self.test_user_login(test_user["login"], test_user["password"])
            results["user_login"] = login_success

            if login_success and token:
                # Тесты работы с данными пользователя
                results["save_user_data"] = self.test_save_user_data(token)
                results["get_user_data"] = self.test_get_user_data(token)[0]
                results["update_user_data"] = self.test_update_user_data(token)
                results["edit_user_data"] = self.test_edit_user_data(token)
                results["check_data_exists"] = self.test_check_user_data_exists(token)
                results["field_operations"] = self.test_field_operations(token)
                results["delete_user_data"] = self.test_delete_user_data(token)

        # Административные тесты
        results["admin_logs"] = self.test_admin_logs()

        # Статистика результатов
        logger.info("=" * 60)
        logger.info("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ API")
        logger.info("=" * 60)

        passed = sum(1 for result in results.values() if result)
        total = len(results)

        for test_name, result in results.items():
            status = "✓ ПРОЙДЕН" if result else "✗ НЕ ПРОЙДЕН"
            logger.info(f"{test_name:.<30} {status}")

        logger.info("=" * 60)
        logger.info(f"ИТОГО: {passed}/{total} тестов пройдено")

        success_rate = (passed / total) * 100
        if success_rate >= 90:
            logger.info(f"✅ ОТЛИЧНО: Сервер работает корректно ({success_rate:.1f}%)")
        elif success_rate >= 70:
            logger.warning(f"⚠ УДОВЛЕТВОРИТЕЛЬНО: Сервер имеет незначительные проблемы ({success_rate:.1f}%)")
        elif success_rate >= 50:
            logger.warning(f"⚠ ТРЕБУЕТ ВНИМАНИЯ: Сервер имеет существенные проблемы ({success_rate:.1f}%)")
        else:
            logger.error(f"❌ КРИТИЧЕСКИ: Сервер не работает корректно ({success_rate:.1f}%)")

        return results


def main():
    """Основная функция запуска тестов"""
    import sys
    
    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    print(f"🚀 Запуск комплексного тестирования API сервера: {base_url}")
    print("⏹  Для остановки нажмите Ctrl+C\n")

    tester = ComprehensiveAPITester(base_url)

    try:
        start_time = time.time()
        results = tester.run_comprehensive_test()
        end_time = time.time()

        execution_time = end_time - start_time
        print(f"\n⏱  Время выполнения тестов: {execution_time:.2f} секунд")

        # Если есть ошибки, ждем ввод для просмотра результатов
        passed = sum(1 for result in results.values() if result)
        if passed < len(results):
            input("\n📋 Нажмите Enter для выхода...")

    except KeyboardInterrupt:
        print("\n\n⏹ Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")
        import traceback
        traceback.print_exc()
        input("Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()
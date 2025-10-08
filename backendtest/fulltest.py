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
        # Словарь для хранения результатов тестов
        self.results = {}
        # Хранение данных тестового пользователя
        self.test_user_data = {}

    def _start_test(self, name):
        """Обертка для начала теста."""
        logger.info(f"\n--- Тестирование: {name} ---")

    def make_request(self, endpoint, method="GET", params=None, data=None):
        """Универсальный метод для выполнения запросов с улучшенным логированием."""
        url = f"{self.base_url}{endpoint}"
        try:
            # Увеличено время ожидания для запросов, которые могут обращаться к GEE
            timeout = 60 if "analysis" in endpoint or "image" in endpoint else 30
            
            response = self.session.request(method.upper(), url, params=params, data=data, timeout=timeout)
            response.raise_for_status()  # Вызовет исключение для кодов 4xx/5xx
            return response
        except requests.exceptions.HTTPError as e:
            logger.error(f"✗ HTTP ошибка при запросе к {url}: {e.response.status_code} {e.response.reason}")
            # Пытаемся получить JSON с деталями ошибки
            try:
                logger.error(f"  Детали ответа: {e.response.json()}")
            except json.JSONDecodeError:
                logger.error(f"  Текст ответа: {e.response.text[:200]}")
            return e.response
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Ошибка соединения при запросе к {url}: {e}")
            return None

    def test_health_check(self):
        self._start_test("Проверка здоровья сервера (/health)")
        response = self.make_request("/health")
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                logger.info("✓ Health check пройден успешно.")
                return True
        logger.error("✗ Health check провален.")
        return False

    def test_user_registration(self):
        self._start_test("Регистрация нового пользователя (/add_user)")
        suffix = str(int(time.time()))
        user = {
            "login": f"testuser_{suffix}",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": f"User_{suffix}"
        }

        response = self.make_request("/add_user", method="POST", params=user)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                logger.info(f"✓ Пользователь '{user['login']}' успешно зарегистрирован.")
                self.test_user_data = user
                return True
        logger.error(f"✗ Регистрация пользователя '{user['login']}' провалена.")
        return False

    def test_user_login(self):
        self._start_test("Аутентификация пользователя (/get_token)")
        login = self.test_user_data.get("login")
        password = self.test_user_data.get("password")
        
        response = self.make_request("/get_token", params={"login": login, "password": password})
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data.get("token"):
                token = data["token"]
                logger.info(f"✓ Вход для пользователя '{login}' успешен. Токен получен.")
                self.test_user_data["token"] = token
                return True
        logger.error(f"✗ Аутентификация для '{login}' провалена.")
        return False

    def test_get_user_profile(self):
        self._start_test("Получение профиля пользователя (/users/profile)")
        token = self.test_user_data.get("token")
        
        response = self.make_request("/users/profile", params={"token": token})
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                profile = data.get("user")
                # Строгая проверка соответствия данных
                if (profile and
                        profile.get("login") == self.test_user_data["login"] and
                        profile.get("first_name") == self.test_user_data["first_name"]):
                    logger.info("✓ Профиль пользователя успешно получен и данные корректны.")
                    return True
                else:
                    logger.error("✗ Данные профиля не соответствуют ожидаемым.")
                    return False
        logger.error("✗ Получение профиля пользователя провалено.")
        return False

    def test_saved_fields_operations(self):
        self._start_test("CRUD операции с сохраненными полями (/fields/*)")
        token = self.test_user_data.get("token")
        field_name = f"Test Field {int(time.time())}"
        aoi_data = {"type": "point_radius", "lon": 37.6, "lat": 55.7, "radius_km": 1.5}
        field_id = None

        # 1. Сохранение
        resp_save = self.make_request("/fields/save", method="POST", params={"token": token, "field_name": field_name, "area_of_interest": json.dumps(aoi_data)})
        if not (resp_save and resp_save.status_code == 200 and resp_save.json().get("status") == "success"):
            logger.error("✗ Провал на этапе сохранения поля.")
            return False
        field_id = resp_save.json().get("field", {}).get("id")
        logger.info(f"✓ Поле '{field_name}' успешно сохранено (ID: {field_id}).")

        # 2. Получение списка
        resp_list = self.make_request("/fields/list", params={"token": token})
        if not (resp_list and resp_list.status_code == 200):
            logger.error("✗ Провал на этапе получения списка полей.")
            return False
        fields = resp_list.json().get("fields", [])
        if not any(f.get("id") == field_id for f in fields):
            logger.error("✗ Сохраненное поле не найдено в списке.")
            return False
        logger.info("✓ Список полей получен, созданное поле найдено.")

        # 3. Удаление
        resp_del = self.make_request(f"/fields/{field_id}", method="DELETE", params={"token": token})
        if not (resp_del and resp_del.status_code == 200 and resp_del.json().get("status") == "success"):
            logger.error("✗ Провал на этапе удаления поля.")
            return False
        logger.info(f"✓ Поле ID {field_id} успешно удалено.")

        logger.info("✓ Все операции с сохраненными полями прошли успешно.")
        return True

    def test_analysis_operations(self):
        self._start_test("Операции с анализом (/analysis/*)")
        token = self.test_user_data.get("token")
        lon, lat = 37.6173, 55.7558
        end_date = time.strftime("%Y-%m-%d")
        start_date = time.strftime("%Y-%m-%d", time.gmtime(time.time() - 60*24*60*60))
        analysis_id = None

        # 1. Выполнение анализа по точке
        logger.info("Запуск анализа по точке и радиусу...")
        resp_perform = self.make_request("/analysis/perform", method="POST", params={"token": token, "lon": lon, "lat": lat, "start_date": start_date, "end_date": end_date})
        
        if not (resp_perform and resp_perform.status_code == 200 and resp_perform.json().get("status") == "success"):
            detail = resp_perform.json().get('detail', '') if resp_perform else 'No response'
            # Если нет снимков, это не ошибка кода, а проблема данных GEE.
            if "Не найдено чистых снимков" in detail:
                 logger.warning("⚠ Анализ пропущен: не найдено подходящих снимков в GEE. Это не является ошибкой сервера.")
                 # Считаем тест условно пройденным (пропущенным), чтобы не ломать всю цепочку
                 return "skipped"
            logger.error("✗ Провал на этапе выполнения анализа.")
            return False
        
        analysis_id = resp_perform.json().get("analysis_id")
        logger.info(f"✓ Анализ успешно запущен (ID: {analysis_id}).")

        # 2. Получение списка анализов
        resp_list = self.make_request("/analysis/list", params={"token": token})
        if not (resp_list and resp_list.status_code == 200 and any(a.get("analysis_id") == analysis_id for a in resp_list.json().get("analyses", []))):
            logger.error("✗ Провал на этапе получения списка анализов.")
            return False
        logger.info("✓ Список анализов получен, созданный анализ найден.")

        # 3. Получение конкретного анализа
        resp_get = self.make_request(f"/analysis/{analysis_id}", params={"token": token})
        if not (resp_get and resp_get.status_code == 200 and resp_get.json().get("status") == "success"):
            logger.error("✗ Провал на этапе получения конкретного анализа.")
            return False
        logger.info(f"✓ Анализ ID {analysis_id} успешно получен.")

        # 4. Удаление анализа
        resp_del = self.make_request(f"/analysis/{analysis_id}", method="DELETE", params={"token": token})
        if not (resp_del and resp_del.status_code == 200 and resp_del.json().get("status") == "success"):
            logger.error("✗ Провал на этапе удаления анализа.")
            return False
        logger.info(f"✓ Анализ ID {analysis_id} успешно удален.")
        
        logger.info("✓ Все операции с анализом прошли успешно.")
        return True

    def test_get_all_users_admin(self):
        self._start_test("Получение списка всех пользователей (админ, /users/all)")
        response = self.make_request("/users/all", params={"password": "12345"})
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                users = data.get("users", [])
                if any(u.get("login") == self.test_user_data["login"] for u in users):
                    logger.info(f"✓ Список пользователей получен ({len(users)} записей), тестовый пользователь найден.")
                    return True
                else:
                    logger.error(f"✗ Созданный пользователь {self.test_user_data['login']} не найден в списке.")
                    return False
        logger.error("✗ Получение списка всех пользователей провалено.")
        return False
        
    def test_admin_logs(self):
        self._start_test("Получение логов (админ, /log)")
        response = self.make_request("/log", params={"password": "12345"})
        if response and response.status_code == 200 and len(response.text) > 10:
             logger.info(f"✓ Логи успешно получены (размер: {len(response.content)} байт).")
             return True
        logger.error("✗ Получение логов провалено.")
        return False

    def test_error_handling(self):
        self._start_test("Обработка ошибок (невалидный токен, 404)")
        # Неверный токен
        resp_token = self.make_request("/users/profile", params={"token": "invalid_token_123"})
        if not (resp_token and resp_token.status_code == 200 and resp_token.json().get("status") == "error"):
            logger.error("✗ Некорректная обработка невалидного токена.")
            return False
        logger.info("✓ Корректная обработка невалидного токена.")

        # Несуществующий эндпоинт
        resp_404 = self.make_request("/nonexistent/endpoint")
        if not (resp_404 and resp_404.status_code == 404):
            logger.error("✗ Некорректная обработка несуществующего эндпоинта (ожидался 404).")
            return False
        logger.info("✓ Корректная обработка несуществующего эндпоинта (404).")

        return True


    def run_comprehensive_test(self):
        """Запуск комплексного тестирования с логической последовательностью."""
        logger.info("=" * 60)
        logger.info("      ЗАПУСК КОМПЛЕКСНОГО ТЕСТИРОВАНИЯ СЕРВЕРА")
        logger.info("=" * 60)
        
        # --- Базовые тесты ---
        self.results["health_check"] = self.test_health_check()

        # --- Блок тестов пользователя (с зависимостями) ---
        if self.test_user_registration():
            self.results["user_registration"] = True
            
            if self.test_user_login():
                self.results["user_login"] = True
                
                # Тесты, требующие валидного токена
                self.results["get_user_profile"] = self.test_get_user_profile()
                self.results["saved_fields_operations"] = self.test_saved_fields_operations()
                
                analysis_result = self.test_analysis_operations()
                if analysis_result == "skipped":
                    self.results["analysis_operations"] = "skipped"
                else:
                    self.results["analysis_operations"] = analysis_result
                    
            else:
                self.results["user_login"] = False
        else:
            self.results["user_registration"] = False
            
        # --- Блок тестов администратора (независимые, но лучше после создания юзера) ---
        if self.test_user_data.get("login"):
             self.results["get_all_users_admin"] = self.test_get_all_users_admin()
        
        self.results["admin_logs"] = self.test_admin_logs()
        self.results["error_handling"] = self.test_error_handling()

        # --- Итоговый отчет ---
        self.print_summary()


    def print_summary(self):
        """Печатает красивый и информативный итоговый отчет."""
        logger.info("=" * 60)
        logger.info("                РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        logger.info("=" * 60)

        passed = []
        failed = []
        skipped = []

        for name, result in self.results.items():
            name_str = name.replace('_', ' ').capitalize()
            if result is True:
                passed.append(name_str)
            elif result == "skipped":
                skipped.append(name_str)
            else:
                failed.append(name_str)
        
        if passed:
            logger.info("\n--- ✓ ПРОЙДЕННЫЕ ТЕСТЫ ---")
            for name in passed: logger.info(f"  - {name}")
        
        if skipped:
            logger.info("\n--- ⚠ ПРОПУЩЕННЫЕ ТЕСТЫ ---")
            for name in skipped: logger.info(f"  - {name}")
            
        if failed:
            logger.info("\n--- ✗ ПРОВАЛЕННЫЕ ТЕСТЫ ---")
            for name in failed: logger.info(f"  - {name}")
        
        total = len(self.results)
        passed_count = len(passed)
        
        logger.info("\n" + "-" * 60)
        logger.info(f"ИТОГО: {passed_count} из {total} тестов пройдено ({len(failed)} провалено, {len(skipped)} пропущено).")
        logger.info("-" * 60)

        success_rate = (passed_count / total) * 100 if total > 0 else 0
        if not failed:
            logger.info(f"★★★★★ ОТЛИЧНО! Все тесты пройдены. ({success_rate:.1f}%) ★★★★★")
        elif success_rate >= 70:
            logger.warning(f"⚠ СЕРВЕР РАБОТАЕТ, НО ЕСТЬ ПРОБЛЕМЫ ({success_rate:.1f}%)")
        else:
            logger.error(f"✗ КРИТИЧЕСКИЕ ОШИБКИ! СЕРВЕР НЕ РАБОТАЕТ КОРРЕКТНО ({success_rate:.1f}%)")


def main():
    """Основная функция"""
    import sys

    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    print(f"\nТестирование сервера по адресу: {base_url}")
    print("Для остановки нажмите Ctrl+C\n")

    tester = ServerTester(base_url)

    try:
        tester.run_comprehensive_test()
        if any(res is False for res in tester.results.values()):
            input("\nТестирование завершено с ошибками. Нажмите Enter для выхода...")

    except KeyboardInterrupt:
        print("\n\nТестирование прервано пользователем.")
    except Exception as e:
        logger.critical(f"\nПроизошла критическая ошибка во время тестирования: {e}", exc_info=True)
        input("Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()
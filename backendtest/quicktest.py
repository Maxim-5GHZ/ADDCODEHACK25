# quick_test.py
import requests
import time


def quick_test():
    """Быстрый тест основных функций сервера"""
    base_url = "http://localhost:8000"

    print("Быстрый тест сервера")
    print("=" * 30)

    # Проверка здоровья
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Health check: {'✓' if response.status_code == 200 else '✗'} {response.status_code}")
    except:
        print("Health check: ✗ Сервер недоступен")
        return

    # Создание тестового пользователя
    test_user = f"test_{int(time.time())}"
    response = requests.post(f"{base_url}/add_user", params={
        "login": test_user,
        "password": "test123"
    })

    if response.status_code == 200 and response.json().get("status") == "success":
        print(f"Регистрация: ✓ Пользователь {test_user} создан")

        # Получение токена
        response = requests.get(f"{base_url}/get_token", params={
            "login": test_user,
            "password": "test123"
        })

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                token = data.get("token")
                print(f"Авторизация: ✓ Токен получен")

                # Сохранение данных
                response = requests.post(f"{base_url}/savedata", params={
                    "token": token,
                    "key_array": "test,data,keys"
                })

                if response.status_code == 200 and response.json().get("status") == "success":
                    print("Сохранение данных: ✓ Успешно")
                else:
                    print("Сохранение данных: ✗ Ошибка")
            else:
                print("Авторизация: ✗ Ошибка")
        else:
            print("Авторизация: ✗ Ошибка запроса")
    else:
        print("Регистрация: ✗ Ошибка")

    print("=" * 30)
    print("Тест завершен")


if __name__ == "__main__":
    quick_test()
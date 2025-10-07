| Имя запроса | Метод | Описание | Пример fetch запроса |
|-------------|--------|-----------|---------------------|
| **Получение токена авторизации** | GET | Аутентификация пользователя и получение токена | `fetch(/get_token?login=${encodeURIComponent(login)}&password=${encodeURIComponent(password)})` |
| **Регистрация нового пользователя** | POST | Создание нового аккаунта пользователя | `fetch(/add_user?login=${encodeURIComponent(login)}&password=${encodeURIComponent(password)}, {method: 'POST'})` |
| **Сохранение данных пользователя** | POST | Сохранение массива ключей пользователя | `fetch(/savedata?token=${encodeURIComponent(token)}&key_array=${encodeURIComponent(keyArray)}, {method: 'POST'})` |
| **Получение данных пользователя** | GET | Получение всех полей пользователя | `fetch(/givefield?token=${encodeURIComponent(token)})` |
| **Получение логов администратора** | GET | Просмотр логов сервера (требует пароль) | `fetch(/log?password=${encodeURIComponent(password)})` |
| **Проверка здоровья сервера** | GET | Проверка работоспособности сервера | `fetch('/health')` |
| **Получение главной страницы** | GET | Загрузка основной HTML страницы | `fetch('/')` |
| **Получение favicon** | GET | Загрузка иконки сайта | `fetch('/favicon.ico')` |
| **Получение статических файлов** | GET | Загрузка файлов из директории scr | `fetch(/scr/${encodeURIComponent(filename)})` |
| **Обновление данных пользователя** | PUT | Полное обновление данных пользователя | `fetch(/data/update?token=${token}&key_array=${keyArray}, {method: 'PUT'})` |
| **Частичное редактирование данных** | PATCH | Частичное обновление данных пользователя | `fetch(/data/edit?token=${token}&new_keys=${newKeys}&keys_to_add=${keysToAdd}&keys_to_remove=${keysToRemove}, {method: 'PATCH'})` |
| **Удаление данных пользователя** | DELETE | Удаление всех данных пользователя | `fetch(/data/delete?token=${token}, {method: 'DELETE'})` |
| **Проверка существования данных** | GET | Проверка наличия данных пользователя | `fetch(/data/check?token=${token})` |
| **Установка данных поля** | POST | Установка значения конкретного поля | `fetch(/field/set?field=${encodeURIComponent(field)}&data=${encodeURIComponent(data)}&token=${encodeURIComponent(token)}, {method: 'POST'})` |
| **Получение данных поля** | GET | Получение значения конкретного поля | `fetch(/field/get?field=${encodeURIComponent(field)}&token=${encodeURIComponent(token)})` |
| **Удаление данных поля** | DELETE | Удаление конкретного поля | `fetch(/field/delete?field=${encodeURIComponent(field)}&token=${encodeURIComponent(token)}, {method: 'DELETE'})` |
| **Проверка существования поля** | GET | Проверка наличия конкретного поля | `fetch(/field/check?field=${encodeURIComponent(field)}&token=${encodeURIComponent(token)})` |
| **Получение RGB изображения** | GET | Получение RGB снимка по геолокации | `fetch(/image/rgb?lon=${lon}&lat=${lat}&start_date=${startDate}&end_date=${endDate}&token=${encodeURIComponent(token)})` |
| **Получение красного канала** | GET | Получение изображения красного канала | `fetch(/image/red-channel?lon=${lon}&lat=${lat}&start_date=${startDate}&end_date=${endDate}&token=${encodeURIComponent(token)})` |
| **Получение NDVI изображения** | GET | Получение NDVI карты растительности | `fetch(/image/ndvi?lon=${lon}&lat=${lat}&start_date=${startDate}&end_date=${endDate}&token=${encodeURIComponent(token)})` |

обнови

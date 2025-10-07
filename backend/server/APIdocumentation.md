Конечно, вот обновленная и дополненная документация по API в формате Markdown.

Я сгруппировал запросы по категориям, добавил недостающие эндпоинты (для управления пользователями и анализами) и уточнил параметры и примеры для всех запросов, включая новый функционал анализа по точке или полигону.

***

### Документация по API

| Имя запроса | Метод | Описание | Пример fetch запроса |
| :--- | :--- | :--- | :--- |
| **Общие и серверные запросы** |
| Проверка здоровья сервера | GET | Проверка работоспособности и доступности сервера. | `fetch('/health')` |
| Получение логов (админ) | GET | Просмотр логов сервера (требует пароль администратора). | `fetch(/log?password=${encodeURIComponent(password)})` |
| Получение главной страницы | GET | Загрузка основной HTML страницы приложения. | `fetch('/')` |
| **Аутентификация и управление пользователями** |
| Получение токена | GET | Аутентификация пользователя и получение токена доступа. | `fetch(/get_token?login=${encodeURIComponent(login)}&password=${encodeURIComponent(password)})` |
| Регистрация пользователя | POST | Создание нового аккаунта с именем и фамилией. | `fetch(/add_user?login=${login}&password=${password}&first_name=${fname}&last_name=${lname}, {method: 'POST'})` |
| Получить всех пользователей (админ) | GET | Получение списка всех зарегистрированных пользователей. | `fetch(/users/all?password=${encodeURIComponent(password)})` |
| **Пользовательские данные (массив ключей)** |
| Сохранение/создание данных | POST | Сохранение или создание массива ключей для пользователя. | `fetch(/savedata?token=${token}&key_array=${encodeURIComponent(keyArray)}, {method: 'POST'})` |
| Получение данных | GET | Получение сохраненного массива ключей пользователя. | `fetch(/givefield?token=${encodeURIComponent(token)})` |
| Обновление данных | PUT | Полная замена массива ключей на новый. | `fetch(/data/update?token=${token}&key_array=${newKeyArray}, {method: 'PUT'})` |
| Частичное редактирование | PATCH | Добавление или удаление ключей из существующего массива. | `fetch(/data/edit?token=${token}&keys_to_add=${keysToAdd}&keys_to_remove=${keysToRemove}, {method: 'PATCH'})` |
| Проверка существования данных | GET | Проверка, есть ли у пользователя сохраненные данные. | `fetch(/data/check?token=${token})` |
| Удаление данных | DELETE | Удаление всех данных (массива ключей) пользователя. | `fetch(/data/delete?token=${token}, {method: 'DELETE'})` |
| **Данные полей (ключ-значение)** |
| Установка данных поля | POST | Установка или обновление данных для произвольного поля (ключа). | `fetch(/field/set?field=${field}&data=${data}&token=${token}, {method: 'POST'})` |
| Получение данных поля | GET | Получение данных по названию поля (ключа). | `fetch(/field/get?field=${encodeURIComponent(field)})` |
| Проверка существования поля | GET | Проверка, существует ли поле с указанным именем. | `fetch(/field/check?field=${encodeURIComponent(field)})` |
| Удаление данных поля | DELETE | Удаление поля и его данных по названию. | `fetch(/field/delete?field=${field}&token=${token}, {method: 'DELETE'})` |
| **Получение изображений (устаревшие)** |
| Получение RGB изображения | GET | Получение RGB снимка по геолокации. | `fetch(/image/rgb?lon=${lon}&lat=${lat}&start_date=${start}&end_date=${end}&token=${token})` |
| Получение красного канала | GET | Получение изображения красного канала. | `fetch(/image/red-channel?lon=${lon}&lat=${lat}&start_date=${start}&end_date=${end}&token=${token})` |
| Получение NDVI изображения | GET | Получение NDVI карты растительности. | `fetch(/image/ndvi?lon=${lon}&lat=${lat}&start_date=${start}&end_date=${end}&token=${token})` |
| **Анализ (рекомендуемый способ)** |
| **Выполнить полный анализ** | POST | Запускает полный анализ по **точке и радиусу** ИЛИ по **полигону**. Сохраняет результат. | `// По точке и радиусу` <br> `fetch(/analysis/perform?token=${token}&start_date=${start}&end_date=${end}&lon=${lon}&lat=${lat}&radius_km=${radius}, {method: 'POST'})` <br><br> `// По полигону (координаты - JSON-строка)` <br> `const poly = JSON.stringify([[lon1, lat1], [lon2, lat2], ...]);` <br> `fetch(/analysis/perform?token=${token}&start_date=${start}&end_date=${end}&polygon_coords=${encodeURIComponent(poly)}, {method: 'POST'})` |
| Получить список анализов | GET | Возвращает список всех ранее выполненных анализов для пользователя. | `fetch(/analysis/list?token=${token})` |
| Получить конкретный анализ | GET | Получает полные данные сохраненного анализа по его ID. | `fetch(/analysis/${analysisId}?token=${token})` |
| Удалить анализ | DELETE | Удаляет сохраненный анализ по его ID. | `fetch(/analysis/${analysisId}?token=${token}, {method: 'DELETE'})` |
# --- START OF FILE controller_func.py ---

import random
import logging
from fastapi.responses import FileResponse
import time
from analysis_manager import AnalysisManager
import os
import json
from ImageProvider import ImageProvider
import ee # Добавлен импорт

logger = logging.getLogger(__name__)

class controller_func():
    # --- ИЗМЕНЕНО: Принимаем один объект db_manager ---
    def __init__(self, db_manager):
        self.db = db_manager
        self.analysis_manager = AnalysisManager(db_manager)
    # --- КОНЕЦ ИЗМЕНЕНИЙ ---

    def _get_user_data_object(self, token: str) -> dict:
        """Вспомогательная функция для получения и парсинга данных пользователя."""
        # ИЗМЕНЕНО
        data_str = self.db.get_user_data(token)
        if data_str:
            try:
                data_obj = json.loads(data_str)
                # Убедимся, что все ключи существуют
                if 'analyses' not in data_obj:
                    data_obj['analyses'] = []
                if 'saved_fields' not in data_obj:
                    data_obj['saved_fields'] = []
                return data_obj
            except json.JSONDecodeError:
                logger.warning(f"Не удалось распарсить JSON для токена {token}. Возвращаем пустую структуру.")
                return {'analyses': [], 'saved_fields': []}
        return {'analyses': [], 'saved_fields': []}

    def _save_user_data_object(self, token: str, data_obj: dict) -> bool:
        """Вспомогательная функция для сохранения объекта данных пользователя."""
        try:
            data_str = json.dumps(data_obj)
            # ИЗМЕНЕНО
            return self.db.save_user_data(token, data_str)
        except Exception as e:
            logger.error(f"Ошибка при сериализации и сохранении данных для токена {token}: {e}")
            return False

    # ... (все старые методы от reed__root до delete_analysis остаются без изменений)
    async def reed__root(self):
        logger.info("Запрос главной страницы")
        try:
            return FileResponse("scr/index.html")
        except Exception as e:
            logger.error(f"Ошибка при загрузке index.html: {e}")
            return {"status": "error", "detail": "Файл не найден"}

    async def ico(self):
        logger.debug("Запрос favicon.ico")
        try:
            return FileResponse("scr/favicon.ico")
        except Exception as e:
            logger.warning(f"Favicon не найден: {e}")
            return {"status": "error", "detail": "Favicon не найден"}

    async def health_check(self):
        """Проверка здоровья сервера"""
        return {
            "status": "healthy",
            "message": "Server is running",
            "timestamp": time.time()
        }

    async def get_from_scr(self, file: str):
        logger.info(f"Запрос {file}")
        if os.path.exists(f"scr/{file}"):
            return FileResponse(f"scr/{file}")
        else:
            return {"status": "error", "detail": "Файл не найден"}

    async def save_data_by_token(self, token: str, key_array: str):
        """
        Сохраняет данные пользователя по токену
        """
        logger.info(f"Запрос на сохранение данных для токена: {token}")

        try:
            # ИЗМЕНЕНО
            if not self.db.if_token_exist(token):
                logger.warning(f"Попытка сохранения данных для несуществующего токена: {token}")
                return {
                    "status": "error",
                    "detail": "Токен не найден"
                }
            
            # ИЗМЕНЕНО
            success = self.db.save_user_data(token, key_array)

            if not success:
                logger.error(f"Не удалось сохранить данные для токена: {token}")
                return {
                    "status": "error",
                    "detail": "Не удалось сохранить данные"
                }

            logger.info(f"Данные для токена {token} успешно сохранены")
            return {
                "status": "success",
                "message": "Данные успешно сохранены",
                "token": token
            }

        except Exception as e:
            logger.error(f"Ошибка при сохранении данных для токена {token}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}

    async def get_field_by_token(self, token: str):
        logger.info(f"Запрос данных для токена: {token}")
        try:
            # ИЗМЕНЕНО
            keys = self.db.get_user_data(token)
            if keys is not None:
                return {
                    "status": "success",
                    "keys": keys
                }
            else:
                return {
                    "status": "dismiss",
                    "message": "Данные не найдены"
                }
        except Exception as e:
            logger.error(f"Ошибка при получении данных для токена {token}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}

    async def get_log(self, password: str):
        logger.info("Запрос логов администратора")
        try:
            if password == "12345":
                return FileResponse("scr/app.log")
            else:
                return {
                    "status": "error",
                    "detail": "Доступ запрещен"
                }
        except Exception as e:
            logger.error(f"Ошибка при чтении логов: {e}")
            return {"status": "error", "detail": "Файл логов не найден"}

    async def get_token(self, login: str, password: str):
        logger.info(f"Запрос токена для пользователя: {login}")
        try:
            # ИЗМЕНЕНО
            token = self.db.get_token(login, password)

            if token is None:
                # ИЗМЕНЕНО
                if not self.db.user_exists(login):
                    logger.warning(f"Пользователь не найден: {login}")
                    return {
                        "status": "error",
                        "detail": "Пользователь не найден"
                    }
                else:
                    logger.warning(f"Неверный пароль для пользователя: {login}")
                    return {
                        "status": "error",
                        "detail": "Неверный пароль"
                    }

            logger.info(f"Токен успешно выдан для пользователя: {login}")
            return {
                "status": "success",
                "token": token,
                "message": "Токен успешно получен"
            }
        except Exception as e:
            logger.error(f"Ошибка в get_token для {login}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}

    async def add_user(self, login: str, password: str, first_name: str, last_name: str):
        """
        Добавление нового пользователя с именем и фамилией
        """
        logger.info(f"Запрос на добавление пользователя: {login}")

        try:
            # ИЗМЕНЕНО
            if self.db.user_exists(login):
                logger.warning(f"Попытка регистрации существующего пользователя: {login}")
                return {
                    "status": "error",
                    "detail": "Пользователь с таким логином уже существует"
                }

            logger.info(f"Генерация токена для пользователя: {login}")
            token = str(random.randint(10 * 10 ** 20, 10 * 10 ** 21))
            # ИЗМЕНЕНО
            while self.db.if_token_exist(token):
                logger.debug(f"Токен {token} уже существует, генерируем новый")
                token = str(random.randint(10 * 10 ** 20, 10 * 10 ** 21))

            logger.info(f"Добавление пользователя {login} с токеном: {token}")
            # ИЗМЕНЕНО
            success = self.db.add_new_user(login, password, token, first_name, last_name)

            if not success:
                logger.error(f"Не удалось добавить пользователя: {login}")
                return {
                    "status": "error",
                    "detail": "Не удалось добавить пользователя"
                }

            logger.info(f"Пользователь {login} успешно зарегистрирован")
            return {
                "status": "success",
                "message": "Пользователь успешно добавлен",
                "login": login,
                "first_name": first_name,
                "last_name": last_name
            }
        except Exception as e:
            logger.error(f"Ошибка в add_user для {login}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}

    async def get_all_users(self, password: str):
        """Получение списка всех пользователей (только для администратора)"""
        logger.info("Запрос списка всех пользователей")
        try:
            if password != "12345":
                logger.warning("Неудачная попытка доступа к списку пользователей")
                return {
                    "status": "error",
                    "detail": "Доступ запрещен"
                }
            
            # ИЗМЕНЕНО
            users_list = self.db.get_all_users()
            return {
                "status": "success",
                "users": users_list
            }

        except Exception as e:
            logger.error(f"Ошибка при получении списка пользователей: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}

    async def get_user_profile(self, token: str):
        """Получение данных профиля пользователя по токену."""
        logger.info(f"Запрос профиля пользователя по токену: {token}")
        try:
            # ИЗМЕНЕНО
            user_info = self.db.get_user_info_by_token(token)

            if user_info:
                return {
                    "status": "success",
                    "user": user_info
                }
            else:
                logger.warning(f"Профиль не найден для токена: {token}")
                return {
                    "status": "error",
                    "detail": "Токен недействителен или пользователь не найден"
                }
        except Exception as e:
            logger.error(f"Ошибка при получении профиля пользователя: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}

    # Методы /data/... теперь работают через _get/save_user_data_object, которые уже обновлены
    async def update_user_data(self, token: str, key_array: str):
        logger.info(f"Запрос на обновление данных для токена: {token}")
        try:
            success = self.db.save_user_data(token, key_array)
            if success:
                return {"status": "success", "message": "Данные успешно обновлены", "token": token}
            else:
                return {"status": "error", "detail": "Токен не найден или данные не обновлены"}
        except Exception as e:
            logger.error(f"Ошибка при обновлении данных для токена {token}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}

    async def edit_user_data(self, token: str, new_keys: str = None, keys_to_add: str = None, keys_to_remove: str = None):
        logger.info(f"Запрос на редактирование данных для токена: {token}")
        try:
            current_data_str = self.db.get_user_data(token)
            if current_data_str is None:
                return {"status": "error", "detail": "Токен не найден"}

            # Эта логика редактирования строки очень специфична и оставлена как есть
            current_key_array = current_data_str
            if new_keys is not None:
                updated_key_array = new_keys
            else:
                updated_key_array = current_key_array
                if keys_to_add:
                    current_keys = set(updated_key_array.split(',')) if updated_key_array else set()
                    keys_to_add_set = set(keys_to_add.split(','))
                    updated_key_array = ','.join(current_keys.union(keys_to_add_set))
                if keys_to_remove:
                    current_keys = set(updated_key_array.split(',')) if updated_key_array else set()
                    keys_to_remove_set = set(keys_to_remove.split(','))
                    updated_key_array = ','.join(current_keys - keys_to_remove_set) if (current_keys - keys_to_remove_set) else ""
            
            success = self.db.save_user_data(token, updated_key_array)
            if success:
                return {"status": "success", "message": "Данные успешно отредактированы", "token": token}
            else:
                return {"status": "error", "detail": "Не удалось отредактировать данные"}
        except Exception as e:
            logger.error(f"Ошибка при редактировании данных для токена {token}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}


    async def delete_user_data(self, token: str):
        logger.info(f"Запрос на удаление данных для токена: {token}")
        try:
            # Удаляем, сохраняя пустой объект JSON
            success = self.db.save_user_data(token, '{}')
            if success:
                return {"status": "success", "message": "Данные успешно удалены", "token": token}
            else:
                return {"status": "error", "detail": "Токен не найден"}
        except Exception as e:
            logger.error(f"Ошибка при удалении данных для токена {token}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}


    async def check_user_data_exists(self, token: str):
        logger.info(f"Запрос проверки данных для токена: {token}")
        try:
            data = self.db.get_user_data(token)
            exists = data is not None and data != '{}'
            return {"status": "success", "exists": exists, "token": token}
        except Exception as e:
            logger.error(f"Ошибка при проверке данных для токена {token}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}

    # Методы /field/... теперь работают с generic_data в новой БД
    async def set_field_data(self, field: str, data: str, token: str):
        logger.info(f"Запрос на установку данных для поля: {field}")
        try:
            if not self.db.if_token_exist(token):
                return {"status": "error", "detail": "Невалидный токен"}

            success = self.db.save_generic_data(field, data)
            if success:
                return {"status": "success", "message": "Данные поля успешно сохранены", "field": field}
            else:
                return {"status": "error", "detail": "Не удалось сохранить данные поля"}
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных для поля {field}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}

    async def get_field_data(self, field: str, token: str = None):
        logger.info(f"Запрос данных для поля: {field}")
        try:
            if token and not self.db.if_token_exist(token):
                return {"status": "error", "detail": "Невалидный токен"}

            data = self.db.get_generic_data(field)
            if data is not None:
                return {"status": "success", "field": field, "data": data}
            else:
                return {"status": "dismiss", "message": "Данные поля не найдены", "field": field}
        except Exception as e:
            logger.error(f"Ошибка при получении данных для поля {field}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}

    async def delete_field_data(self, field: str, token: str):
        logger.info(f"Запрос на удаление данных поля: {field}")
        try:
            if not self.db.if_token_exist(token):
                return {"status": "error", "detail": "Невалидный токен"}

            success = self.db.delete_generic_data(field)
            if success:
                return {"status": "success", "message": "Данные поля успешно удалены", "field": field}
            else:
                return {"status": "error", "detail": "Поле не найдено"}
        except Exception as e:
            logger.error(f"Ошибка при удалении данных поля {field}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}

    async def check_field_exists(self, field: str, token: str = None):
        logger.info(f"Запрос проверки существования поля: {field}")
        try:
            if token and not self.db.if_token_exist(token):
                return {"status": "error", "detail": "Невалидный токен"}

            exists = self.db.generic_data_exists(field)
            return {"status": "success", "field": field, "exists": exists}
        except Exception as e:
            logger.error(f"Ошибка при проверке поля {field}: {e}")
            return {"status": "error", "detail": "Внутренняя ошибка сервера"}
        
    async def get_rgb_image(self, lon: float, lat: float, start_date: str, end_date: str, token: str):
        """Получение RGB изображения по геолокации"""
        logger.info(f"Запрос RGB изображения для координат: {lon}, {lat}")

        try:
            # ИЗМЕНЕНО
            if not self.db.if_token_exist(token):
                logger.warning(f"Попытка получения изображения с невалидным токеном: {token}")
                return {
                    "status": "error",
                    "detail": "Невалидный токен"
                }

            # Получаем изображение через ImageProvider
            provider = ImageProvider.from_gee(
                lon=lon,
                lat=lat,
                start_date=start_date,
                end_date=end_date
            )

            # Конвертируем RGB изображение в base64
            import base64
            from io import BytesIO
            from PIL import Image
            
            # Конвертируем numpy array в PIL Image
            rgb_image_pil = Image.fromarray(provider.rgb_image.astype('uint8'))
            
            # Конвертируем в base64
            buffered = BytesIO()
            rgb_image_pil.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            logger.info(f"RGB изображение успешно получено для координат: {lon}, {lat}")
            return {
                "status": "success",
                "image_type": "rgb",
                "image_data": img_str,
                "format": "jpeg",
                "coordinates": {"lon": lon, "lat": lat},
                "date_range": {"start": start_date, "end": end_date}
            }

        except Exception as e:
            logger.error(f"Ошибка при получении RGB изображения: {e}")
            return {
                "status": "error",
                "detail": f"Не удалось получить изображение: {str(e)}"
            }

    async def get_red_channel_image(self, lon: float, lat: float, start_date: str, end_date: str, token: str):
        """Получение изображения красного канала по геолокации"""
        logger.info(f"Запрос красного канала для координат: {lon}, {lat}")

        try:
            # ИЗМЕНЕНО
            if not self.db.if_token_exist(token):
                logger.warning(f"Попытка получения изображения с невалидным токеном: {token}")
                return {
                    "status": "error",
                    "detail": "Невалидный токен"
                }

            # Получаем изображение через ImageProvider
            provider = ImageProvider.from_gee(
                lon=lon,
                lat=lat,
                start_date=start_date,
                end_date=end_date
            )

            # Нормализуем красный канал для визуализации
            red_channel_normalized = (provider.red_channel - provider.red_channel.min()) / (provider.red_channel.max() - provider.red_channel.min()) * 255
            red_channel_uint8 = red_channel_normalized.astype('uint8')

            # Конвертируем в base64
            import base64
            from io import BytesIO
            from PIL import Image
            
            red_image_pil = Image.fromarray(red_channel_uint8)
            
            buffered = BytesIO()
            red_image_pil.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            logger.info(f"Красный канал успешно получен для координат: {lon}, {lat}")
            return {
                "status": "success",
                "image_type": "red_channel",
                "image_data": img_str,
                "format": "jpeg",
                "coordinates": {"lon": lon, "lat": lat},
                "date_range": {"start": start_date, "end": end_date},
                "statistics": {
                    "min_value": float(provider.red_channel.min()),
                    "max_value": float(provider.red_channel.max()),
                    "mean_value": float(provider.red_channel.mean())
                }
            }

        except Exception as e:
            logger.error(f"Ошибка при получении красного канала: {e}")
            return {
                "status": "error",
                "detail": f"Не удалось получить изображение: {str(e)}"
            }

    async def get_ndvi_image(self, lon: float, lat: float, start_date: str, end_date: str, token: str):
        """Получение NDVI изображения по геолокации"""
        logger.info(f"Запрос NDVI для координат: {lon}, {lat}")

        try:
            # ИЗМЕНЕНО
            if not self.db.if_token_exist(token):
                logger.warning(f"Попытка получения NDVI с невалидным токеном: {token}")
                return {
                    "status": "error",
                    "detail": "Невалидный токен"
                }

            # Получаем изображение через ImageProvider
            provider = ImageProvider.from_gee(
                lon=lon,
                lat=lat,
                start_date=start_date,
                end_date=end_date
            )

            # Вычисляем NDVI
            ndvi = (provider.nir_channel - provider.red_channel) / (provider.nir_channel + provider.red_channel + 1e-8)
            
            # Нормализуем NDVI от -1 до 1 для визуализации
            ndvi_normalized = ((ndvi + 1) / 2 * 255).clip(0, 255).astype('uint8')

            # Конвертируем в base64
            import base64
            from io import BytesIO
            from PIL import Image
            
            ndvi_image_pil = Image.fromarray(ndvi_normalized)
            
            buffered = BytesIO()
            ndvi_image_pil.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            logger.info(f"NDVI успешно получен для координат: {lon}, {lat}")
            return {
                "status": "success",
                "image_type": "ndvi",
                "image_data": img_str,
                "format": "jpeg",
                "coordinates": {"lon": lon, "lat": lat},
                "date_range": {"start": start_date, "end": end_date},
                "statistics": {
                    "min_ndvi": float(ndvi.min()),
                    "max_ndvi": float(ndvi.max()),
                    "mean_ndvi": float(ndvi.mean())
                }
            }

        except Exception as e:
            logger.error(f"Ошибка при получении NDVI: {e}")
            return {
                "status": "error",
                "detail": f"Не удалось вычислить NDVI: {str(e)}"
            }
    async def perform_analysis(self, token: str, start_date: str, end_date: str,
                             lon: float = None, lat: float = None,
                             radius_km: float = 0.5,
                             polygon_coords: str = None):
        """Выполняет полный анализ по координатам точки с радиусом или по полигону."""
        logger.info(f"Запрос полного анализа для токена {token}")

        try:
            # ИЗМЕНЕНО
            if not self.db.if_token_exist(token):
                logger.warning(f"Попытка анализа с невалидным токеном: {token}")
                return {"status": "error", "detail": "Невалидный токен"}

            parsed_polygon_coords = None
            if polygon_coords:
                try:
                    parsed_polygon_coords = json.loads(polygon_coords)
                    if not isinstance(parsed_polygon_coords, list) or not all(
                            isinstance(p, list) and len(p) == 2 and all(
                                isinstance(coord, (int, float)) for coord in p) for p in parsed_polygon_coords):
                        raise ValueError("polygon_coords должен быть списком списков координат [[lon, lat], ...]")
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"Ошибка парсинга polygon_coords='{polygon_coords}': {e}")
                    return {"status": "error", "detail": f"Неверный формат polygon_coords: {e}"}
            
            result = self.analysis_manager.perform_complete_analysis(
                token=token, start_date=start_date, end_date=end_date, lon=lon,
                lat=lat, radius_km=radius_km, polygon_coords=parsed_polygon_coords
            )

            return result

        except Exception as e:
            logger.error(f"Ошибка при выполнении анализа: {e}")
            return {"status": "error", "detail": f"Не удалось выполнить анализ: {str(e)}"}

    async def get_analyses_list(self, token: str):
        """Получает список всех анализов пользователя"""
        logger.info(f"Запрос списка анализов для токена: {token}")
        try:
            # ИЗМЕНЕНО
            if not self.db.if_token_exist(token):
                return {"status": "error", "detail": "Невалидный токен"}
            
            user_data_obj = self._get_user_data_object(token)
            return {"status": "success", "analyses": user_data_obj.get('analyses', [])}

        except Exception as e:
            logger.error(f"Ошибка при получении списка анализов: {e}")
            return {"status": "error", "detail": str(e)}

    async def get_analysis(self, token: str, analysis_id: str):
        """Получает конкретный анализ по ID"""
        logger.info(f"Запрос анализа {analysis_id} для токена: {token}")
        try:
            # ИЗМЕНЕНО
            if not self.db.if_token_exist(token):
                return {"status": "error", "detail": "Невалидный токен"}

            result = self.analysis_manager.get_analysis_by_id(token, analysis_id)
            return result
        except Exception as e:
            logger.error(f"Ошибка при получении анализа: {e}")
            return {"status": "error", "detail": str(e)}

    async def delete_analysis(self, token: str, analysis_id: str):
        """Удаляет анализ"""
        logger.info(f"Запрос удаления анализа {analysis_id} для токена: {token}")
        try:
            # ИЗМЕНЕНО
            if not self.db.if_token_exist(token):
                return {"status": "error", "detail": "Невалидный токен"}

            result = self.analysis_manager.delete_analysis(token, analysis_id)
            return result
        except Exception as e:
            logger.error(f"Ошибка при удалении анализа: {e}")
            return {"status": "error", "detail": str(e)}

    # --- НОВЫЙ МЕТОД ---
    async def get_historical_ndvi_data(self, token: str, 
                                       lon: float = None, lat: float = None,
                                       radius_km: float = 0.5,
                                       polygon_coords: str = None):
        """Возвращает историю среднего NDVI для области."""
        logger.info(f"Запрос истории NDVI для токена {token}")
        
        # ИЗМЕНЕНО
        if not self.db.if_token_exist(token):
            return {"status": "error", "detail": "Невалидный токен"}

        try:
            # Определяем область интереса для GEE
            if polygon_coords:
                parsed_polygon = json.loads(polygon_coords)
                area_of_interest = ee.Geometry.Polygon(parsed_polygon)
            elif lon is not None and lat is not None:
                point = ee.Geometry.Point([lon, lat])
                area_of_interest = point.buffer(radius_km * 1000).bounds()
            else:
                return {"status": "error", "detail": "Необходимо указать область"}

            # Используем новый статический метод
            # Берем данные за последние 2 года
            import datetime
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=365*2)
            
            historical_data = ImageProvider.get_historical_ndvi(
                area_of_interest, 
                start_date.strftime('%Y-%m-%d'), 
                end_date.strftime('%Y-%m-%d')
            )

            return {
                "status": "success",
                "data": historical_data
            }

        except Exception as e:
            logger.error(f"Ошибка при получении истории NDVI: {e}")
            return {"status": "error", "detail": f"Не удалось получить историю: {e}"}

    # --- НОВЫЕ МЕТОДЫ ДЛЯ УПРАВЛЕНИЯ ПОЛЯМИ ---
    async def save_user_field(self, token: str, field_name: str, area_of_interest: str):
        """Сохраняет новое поле для пользователя."""
        logger.info(f"Запрос сохранения поля '{field_name}' для токена {token}")
        try:
            # ИЗМЕНЕНО
            if not self.db.if_token_exist(token):
                return {"status": "error", "detail": "Невалидный токен"}

            try:
                aoi_data = json.loads(area_of_interest)
            except json.JSONDecodeError:
                return {"status": "error", "detail": "Неверный формат area_of_interest"}

            user_data_obj = self._get_user_data_object(token)
            
            new_field = {
                "id": str(int(time.time())),
                "name": field_name,
                "area_of_interest": aoi_data
            }
            
            user_data_obj['saved_fields'].insert(0, new_field)

            if self._save_user_data_object(token, user_data_obj):
                return {"status": "success", "message": "Поле успешно сохранено", "field": new_field}
            else:
                return {"status": "error", "detail": "Не удалось сохранить данные"}

        except Exception as e:
            logger.error(f"Ошибка при сохранении поля: {e}")
            return {"status": "error", "detail": f"Внутренняя ошибка сервера: {e}"}

    async def get_user_fields(self, token: str):
        """Получает список сохраненных полей пользователя."""
        logger.info(f"Запрос списка полей для токена {token}")
        try:
            # ИЗМЕНЕНО
            if not self.db.if_token_exist(token):
                return {"status": "error", "detail": "Невалидный токен"}

            user_data_obj = self._get_user_data_object(token)
            return {"status": "success", "fields": user_data_obj.get('saved_fields', [])}

        except Exception as e:
            logger.error(f"Ошибка при получении списка полей: {e}")
            return {"status": "error", "detail": f"Внутренняя ошибка сервера: {e}"}

    async def delete_user_field(self, token: str, field_id: str):
        """Удаляет сохраненное поле пользователя по ID."""
        logger.info(f"Запрос удаления поля ID {field_id} для токена {token}")
        try:
            # ИЗМЕНЕНО
            if not self.db.if_token_exist(token):
                return {"status": "error", "detail": "Невалидный токен"}

            user_data_obj = self._get_user_data_object(token)
            
            initial_count = len(user_data_obj['saved_fields'])
            user_data_obj['saved_fields'] = [
                field for field in user_data_obj['saved_fields'] if field.get('id') != field_id
            ]
            
            if len(user_data_obj['saved_fields']) == initial_count:
                return {"status": "error", "detail": "Поле с таким ID не найдено"}

            if self._save_user_data_object(token, user_data_obj):
                return {"status": "success", "message": "Поле успешно удалено"}
            else:
                return {"status": "error", "detail": "Не удалось сохранить изменения"}

        except Exception as e:
            logger.error(f"Ошибка при удалении поля: {e}")
            return {"status": "error", "detail": f"Внутренняя ошибка сервера: {e}"}
# image_provider.py (СУПЕР-ДИАГНОСТИЧЕСКАЯ ВЕРСИЯ)

import os
import cv2
import numpy as np
import requests
import ee
import json


class ImageProvider:
    def __init__(self, rgb_image_path: str = None, nir_image_path: str = None):
        """Инициализация через локальные файлы."""
        self.rgb_image = None
        self.red_channel = None
        self.green_channel = None
        self.blue_channel = None
        self.nir_channel = None
        if rgb_image_path:
            self._load_local_images(rgb_image_path, nir_image_path)

    def _load_local_images(self, rgb_path, nir_path):
        img_bgr = cv2.imread(rgb_path)
        if img_bgr is None:
            raise FileNotFoundError(f"Ошибка: Не удалось загрузить RGB изображение: {rgb_path}")
        self.rgb_image = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        self.red_channel = self.rgb_image[:, :, 0].astype(np.float32)
        self.green_channel = self.rgb_image[:, :, 1].astype(np.float32)
        self.blue_channel = self.rgb_image[:, :, 2].astype(np.float32)
        if nir_path:
            self.nir_channel = cv2.imread(nir_path, cv2.IMREAD_GRAYSCALE).astype(np.float32)
            if self.nir_channel is None:
                raise FileNotFoundError(f"Ошибка: Не удалось загрузить NIR изображение: {nir_path}")
            self._align_images()

    def _align_images(self):
        if self.rgb_image is not None and self.nir_channel is not None:
            if self.rgb_image.shape[:2] != self.nir_channel.shape:
                h, w = self.rgb_image.shape[:2]
                self.nir_channel = cv2.resize(self.nir_channel, (w, h), interpolation=cv2.INTER_AREA)

    @staticmethod
    def _url_to_numpy(url: str) -> np.ndarray:
        """(Статический) Скачивает изображение по URL и конвертирует его в NumPy массив."""
        print(f"\n---[Диагностика _url_to_numpy]---")
        print(f"Пытаюсь скачать данные со ссылки...")
        response = requests.get(url, stream=True)
        print(f"Статус-код ответа сервера: {response.status_code}")

        if response.status_code != 200:
            raise ConnectionError(f"Не удалось скачать изображение. Статус: {response.status_code}")

        # ВЫВОДИМ ПЕРВЫЕ 500 СИМВОЛОВ ОТВЕТА
        content_preview = response.content[:500]
        print(f"Превью ответа сервера (первые 500 байт):\n---\n{content_preview}\n---")

        img_array = np.frombuffer(response.content, np.uint8)
        img_bgr = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img_bgr is None:
            raise ValueError("cv2.imdecode не смог распознать данные как изображение. Ответ сервера - не картинка.")

        return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    @classmethod
    def from_gee(cls, lon: float, lat: float, start_date: str, end_date: str, buffer_size_km: float = 0.5,
                 service_account_key_path: str = None):
        """
        Фабричный метод для создания экземпляра класса с НАУЧНЫМИ данными из Google Earth Engine.
        """
        try:
            if service_account_key_path and os.path.exists(service_account_key_path):
                with open(service_account_key_path) as f:
                    credentials_info = json.load(f)
                service_account_email = credentials_info['client_email']
                credentials = ee.ServiceAccountCredentials(service_account_email, service_account_key_path)
                ee.Initialize(credentials=credentials)
            else:
                ee.Initialize()
        except Exception as e:
            raise ConnectionError(f"Ошибка инициализации Earth Engine: {e}")

        point = ee.Geometry.Point([lon, lat])
        area_of_interest = point.buffer(buffer_size_km * 1000).bounds()

        collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                      .filterBounds(area_of_interest)
                      .filterDate(start_date, end_date)
                      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 70)))

        count = collection.size().getInfo()
        print(f"Найдено изображений в коллекции: {count}")
        if count == 0:
            raise FileNotFoundError("Не найдено чистых снимков. Попробуйте расширить диапазон дат.")

        bands = ['B2', 'B3', 'B4', 'B8']
        image = collection.select(bands).median().clip(area_of_interest)

        provider = cls()
        print("Загрузка данных из Google Earth Engine...")

        try:
            # --- ГЛАВНОЕ ИСПРАВЛЕНИЕ ЗДЕСЬ ---
            # Добавляем параметр 'dimensions', чтобы указать GEE размер итоговой картинки.
            rgb_vis_params = {
                'bands': ['B4', 'B3', 'B2'],
                'min': 0,
                'max': 3000,
                'dimensions': 512  # Создать картинку размером 512x512 пикселей
            }
            provider.rgb_image = cls._url_to_numpy(image.getThumbURL(rgb_vis_params))
            print("Изображение для визуализации успешно создано.")

        except Exception as e:
            provider.rgb_image = np.zeros((100, 100, 3), dtype=np.uint8)
            print(f"Предупреждение: Не удалось создать визуальное изображение. Ошибка: {e}")

        try:
            pixels = image.sampleRectangle(region=area_of_interest, defaultValue=0).getInfo()
            if not pixels['properties'] or not pixels['properties'].get('B4'):
                raise ValueError("После обработки не осталось валидных пикселей для научных данных.")
            provider.red_channel = np.array(pixels['properties']['B4'], dtype=np.float32)
            provider.green_channel = np.array(pixels['properties']['B3'], dtype=np.float32)
            provider.blue_channel = np.array(pixels['properties']['B2'], dtype=np.float32)
            provider.nir_channel = np.array(pixels['properties']['B8'], dtype=np.float32)
        except Exception as e:
            raise ConnectionError(f"КРИТИЧЕСКАЯ ОШИБКА: Не удалось получить научные данные. Причина: {e}")

        print("Данные успешно загружены.")
        return provider
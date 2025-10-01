# image_provider.py

import os
import cv2
import numpy as np
import requests
import ee


class ImageProvider:
    # ... (код этого класса остается без изменений) ...
    """
    Отвечает за предоставление RGB и NIR изображений из разных источников:
    - Локальные файлы
    - Google Earth Engine API
    """

    def __init__(self, rgb_image_path: str = None, nir_image_path: str = None):
        """Инициализация через локальные файлы."""
        self.rgb_image = None
        self.nir_image = None
        if rgb_image_path:
            self._load_local_images(rgb_image_path, nir_image_path)

    def _load_local_images(self, rgb_path, nir_path):
        """(Приватный) Загружает изображения из локальных файлов."""
        img_bgr = cv2.imread(rgb_path)
        if img_bgr is None:
            raise FileNotFoundError(f"Ошибка: Не удалось загрузить RGB изображение: {rgb_path}")
        self.rgb_image = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        if nir_path:
            self.nir_image = cv2.imread(nir_path, cv2.IMREAD_GRAYSCALE)
            if self.nir_image is None:
                raise FileNotFoundError(f"Ошибка: Не удалось загрузить NIR изображение: {nir_path}")
            self._align_images()

    def _align_images(self):
        """(Приватный) Приводит размер NIR к размеру RGB, если они не совпадают."""
        if self.rgb_image is not None and self.nir_image is not None:
            if self.rgb_image.shape[:2] != self.nir_image.shape:
                print("Внимание: Размеры RGB и NIR не совпадают. Приводим NIR к размеру RGB.")
                h, w = self.rgb_image.shape[:2]
                self.nir_image = cv2.resize(self.nir_image, (w, h), interpolation=cv2.INTER_AREA)

    @staticmethod
    def _url_to_numpy(url: str) -> np.ndarray:
        """(Статический) Скачивает изображение по URL и конвертирует его в NumPy массив."""
        response = requests.get(url)
        if response.status_code != 200:
            raise ConnectionError(f"Не удалось скачать изображение. Статус: {response.status_code}")
        img_array = np.frombuffer(response.content, np.uint8)
        img_bgr = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    @classmethod
    def from_gee(cls, lon: float, lat: float, start_date: str, end_date: str, buffer_size: float = 0.01,
                 service_account_key_path: str = None):
        """
        Фабричный метод для создания экземпляра класса с данными из Google Earth Engine.
        """
        try:
            if service_account_key_path and os.path.exists(service_account_key_path):
                print(f"Инициализация GEE с использованием локального ключа: {service_account_key_path}")
                credentials = ee.ServiceAccountCredentials(None, key_file=service_account_key_path)
                ee.Initialize(credentials)
            else:
                print("Локальный ключ не найден. Инициализация GEE со стандартными учетными данными...")
                ee.Initialize()
        except Exception as e:
            raise ConnectionError(f"Ошибка инициализации Earth Engine. Ошибка: {e}")

        point = ee.Geometry.Point([lon, lat])
        area_of_interest = point.buffer(buffer_size * 1000).bounds()
        collection = (ee.ImageCollection('COPERNICUS/S2_SR')
                      .filterBounds(area_of_interest)
                      .filterDate(start_date, end_date)
                      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)))

        if collection.size().getInfo() == 0:
            raise FileNotFoundError("Не найдено чистых снимков для указанного периода.")

        image = collection.mosaic().clip(area_of_interest)
        rgb_params = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000}
        nir_params = {'bands': ['B8'], 'min': 0, 'max': 5000}

        provider = cls()
        print("Загрузка данных из Google Earth Engine...")
        provider.rgb_image = cls._url_to_numpy(image.getThumbURL(rgb_params))
        provider.nir_image = cls._url_to_numpy(image.getThumbURL(nir_params))[:, :, 0]
        print("Данные успешно загружены.")

        provider._align_images()
        return provider
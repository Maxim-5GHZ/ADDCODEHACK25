# image_provider.py

import os
import cv2
import numpy as np
import requests
import ee


class ImageProvider:
    """
    Отвечает за предоставление RGB, Red и NIR каналов из разных источников:
    - Локальные файлы
    - Google Earth Engine API (с использованием точных каналов B04, B08)
    """

    def __init__(self, rgb_image_path: str = None, nir_image_path: str = None):
        """Инициализация через локальные файлы."""
        self.rgb_image = None
        self.red_channel = None
        self.nir_channel = None

        if rgb_image_path:
            self._load_local_images(rgb_image_path, nir_image_path)

    def _load_local_images(self, rgb_path, nir_path):
        """(Приватный) Загружает изображения из локальных файлов."""
        img_bgr = cv2.imread(rgb_path)
        if img_bgr is None:
            raise FileNotFoundError(f"Ошибка: Не удалось загрузить RGB изображение: {rgb_path}")
        self.rgb_image = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        # Для локальных файлов красный канал берем из RGB изображения
        self.red_channel = self.rgb_image[:, :, 0]

        if nir_path:
            self.nir_channel = cv2.imread(nir_path, cv2.IMREAD_GRAYSCALE)
            if self.nir_channel is None:
                raise FileNotFoundError(f"Ошибка: Не удалось загрузить NIR изображение: {nir_path}")
            self._align_images()

    def _align_images(self):
        """(Приватный) Приводит размер NIR канала к размеру RGB, если они не совпадают."""
        if self.rgb_image is not None and self.nir_channel is not None:
            if self.rgb_image.shape[:2] != self.nir_channel.shape:
                print("Внимание: Размеры изображений не совпадают. Приводим NIR к размеру RGB.")
                h, w = self.rgb_image.shape[:2]
                self.nir_channel = cv2.resize(self.nir_channel, (w, h), interpolation=cv2.INTER_AREA)

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

        # Параметры для визуализации (шкалирование значений для получения 8-битного изображения)
        rgb_params = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000}  # B4=Red, B3=Green, B2=Blue
        red_b04_params = {'bands': ['B4'], 'min': 0, 'max': 3000}
        nir_b08_params = {'bands': ['B8'], 'min': 0, 'max': 5000}  # B8=NIR

        provider = cls()
        print("Загрузка данных из Google Earth Engine...")
        # Скачиваем RGB-версию для красивого отображения
        provider.rgb_image = cls._url_to_numpy(image.getThumbURL(rgb_params))
        # Скачиваем точные каналы B04 и B08 для расчетов
        provider.red_channel = cls._url_to_numpy(image.getThumbURL(red_b04_params))[:, :, 0]
        provider.nir_channel = cls._url_to_numpy(image.getThumbURL(nir_b08_params))[:, :, 0]
        print("Данные успешно загружены.")

        provider._align_images()
        return provider
# image_provider.py

import os
import cv2
import numpy as np
import requests
import ee
import json


class ImageProvider:
    """
    Отвечает за предоставление 8-битного RGB (для визуализации) и научных данных
    (Red, Green, Blue, NIR каналов) из разных источников.
    """

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
        """(Приватный) Загружает изображения из локальных файлов."""
        img_bgr = cv2.imread(rgb_path)
        if img_bgr is None:
            raise FileNotFoundError(f"Ошибка: Не удалось загрузить RGB изображение: {rgb_path}")
        self.rgb_image = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        # Для локальных файлов берем каналы из 8-битного RGB
        self.red_channel = self.rgb_image[:, :, 0].astype(np.float32)
        self.green_channel = self.rgb_image[:, :, 1].astype(np.float32)
        self.blue_channel = self.rgb_image[:, :, 2].astype(np.float32)

        if nir_path:
            self.nir_channel = cv2.imread(nir_path, cv2.IMREAD_GRAYSCALE).astype(np.float32)
            if self.nir_channel is None:
                raise FileNotFoundError(f"Ошибка: Не удалось загрузить NIR изображение: {nir_path}")
            self._align_images()

    def _align_images(self):
        """(Приватный) Приводит размер NIR канала к размеру RGB, если они не совпадают."""
        if self.rgb_image is not None and self.nir_channel is not None:
            if self.rgb_image.shape[:2] != self.nir_channel.shape:
                h, w = self.rgb_image.shape[:2]
                self.nir_channel = cv2.resize(self.nir_channel, (w, h), interpolation=cv2.INTER_AREA)

    @staticmethod
    def _url_to_numpy(url: str) -> np.ndarray:
        """(Статический) Скачивает изображение по URL и конвертирует его в NumPy массив."""
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise ConnectionError(f"Не удалось скачать изображение. Статус: {response.status_code}")
        img_array = np.frombuffer(response.content, np.uint8)
        img_bgr = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
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

        # --- ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ ЗДЕСЬ ---
        # Убираем сложный динамический расчет и используем стандартные, надежные параметры.
        # Этот диапазон (0-3000) хорошо подходит для большинства снимков Sentinel-2.
        try:
            print("Используются стандартные параметры визуализации (min: 0, max: 3000).")
            rgb_vis_params = {
                'bands': ['B4', 'B3', 'B2'],
                'min': 0,
                'max': 3000
            }
            provider.rgb_image = cls._url_to_numpy(image.getThumbURL(rgb_vis_params))
        except Exception as e:
            provider.rgb_image = np.zeros((100, 100, 3), dtype=np.uint8)
            print(f"Предупреждение: Не удалось создать визуальное изображение. Ошибка: {e}")

        # Блок получения научных данных уже работает правильно, так как мы видели результат от reduceRegion.
        try:
            pixels = image.sampleRectangle(region=area_of_interest, defaultValue=0).getInfo()
            provider.red_channel = np.array(pixels['properties']['B4'], dtype=np.float32)
            provider.green_channel = np.array(pixels['properties']['B3'], dtype=np.float32)
            provider.blue_channel = np.array(pixels['properties']['B2'], dtype=np.float32)
            provider.nir_channel = np.array(pixels['properties']['B8'], dtype=np.float32)
        except Exception as e:
            raise ConnectionError(f"КРИТИЧЕСКАЯ ОШИБКА: Не удалось получить научные данные. Причина: {e}")

        print("Данные успешно загружены.")
        return provider
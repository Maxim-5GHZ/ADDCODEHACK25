import os
import cv2
import numpy as np
import requests
import ee
import json


class ImageProvider:
    def __init__(self, rgb_image_path: str = None, nir_image_path: str = None):
        self.rgb_image, self.red_channel, self.green_channel, self.blue_channel, self.nir_channel = None, None, None, None, None
        if rgb_image_path: self._load_local_images(rgb_image_path, nir_image_path)

    def _load_local_images(self, rgb_path, nir_path):
        img_bgr = cv2.imread(rgb_path);
        self.rgb_image = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        self.red_channel, self.green_channel, self.blue_channel = self.rgb_image[:, :, 0].astype(np.float32), \
        self.rgb_image[:, :, 1].astype(np.float32), self.rgb_image[:, :, 2].astype(np.float32)
        if nir_path: self.nir_channel = cv2.imread(nir_path, cv2.IMREAD_GRAYSCALE).astype(
            np.float32); self._align_images()

    def _align_images(self):
        if self.rgb_image is not None and self.nir_channel is not None and self.rgb_image.shape[
            :2] != self.nir_channel.shape:
            h, w = self.rgb_image.shape[:2];
            self.nir_channel = cv2.resize(self.nir_channel, (w, h), interpolation=cv2.INTER_AREA)

    @staticmethod
    def _url_to_numpy(url: str) -> np.ndarray:
        response = requests.get(url, stream=True);
        img_array = np.frombuffer(response.content, np.uint8)
        img_bgr = cv2.imdecode(img_array, cv2.IMREAD_COLOR);
        return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    @classmethod
    def from_gee(cls, lon: float, lat: float, start_date: str, end_date: str, buffer_size_km: float = 0.5,
                 service_account_key_path: str = "hack25addcode-3171f61bba2c.json"):
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

        # --- НАДЕЖНЫЙ ПОДХОД: ИСПОЛЬЗУЕМ ОДИН, САМЫЙ ЧИСТЫЙ СНИМОК ---
        collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                      .filterBounds(area_of_interest)
                      .filterDate(start_date, end_date))

        collection_sorted = collection.sort('CLOUDY_PIXEL_PERCENTAGE')

        count = collection_sorted.size().getInfo()
        print(f"Найдено изображений в коллекции: {count}")
        if count == 0:
            raise FileNotFoundError("Не найдено чистых снимков. Попробуйте расширить диапазон дат.")

        # Берем ОДИН, самый чистый снимок, и работаем только с ним
        cleanest_image = ee.Image(collection_sorted.first()).clip(area_of_interest)
        cloud_percentage = cleanest_image.get('CLOUDY_PIXEL_PERCENTAGE').getInfo()
        print(f"Выбран самый чистый снимок с облачностью: {cloud_percentage:.2f}%")

        provider = cls()
        print("Загрузка данных из Google Earth Engine...")

        try:
            rgb_vis_params = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000, 'dimensions': 512}
            provider.rgb_image = cls._url_to_numpy(cleanest_image.getThumbURL(rgb_vis_params))
        except Exception as e:
            provider.rgb_image = np.zeros((100, 100, 3), dtype=np.uint8)
            print(f"Предупреждение: Не удалось создать визуальное изображение. Ошибка: {e}")

        try:
            # Используем самый стандартный и надежный метод sampleRectangle на одном чистом снимке
            pixels = cleanest_image.select(['B2', 'B3', 'B4', 'B8']).sampleRectangle(region=area_of_interest,
                                                                                     defaultValue=0).getInfo()

            if not pixels['properties'] or not pixels['properties'].get('B4'):
                raise ValueError("Научные данные от GEE пришли пустыми.")

            provider.red_channel = np.array(pixels['properties']['B4'], dtype=np.float32)
            provider.green_channel = np.array(pixels['properties']['B3'], dtype=np.float32)
            provider.blue_channel = np.array(pixels['properties']['B2'], dtype=np.float32)
            provider.nir_channel = np.array(pixels['properties']['B8'], dtype=np.float32)

        except Exception as e:
            raise ConnectionError(f"КРИТИЧЕСКАЯ ОШИБКА: Не удалось получить научные данные. Причина: {e}")

        print("Данные успешно загружены.")
        return provider
    

ImageProvider()
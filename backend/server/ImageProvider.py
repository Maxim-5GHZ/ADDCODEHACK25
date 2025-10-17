
import os
import cv2
import numpy as np
import requests
import ee
import json
from typing import List, Dict
from gee_initializer import GEEInitializer


class ImageProvider:
    CLOUD_FILTER_PERCENTAGE = 0.05
    # <<< --- НОВОЕ: Константы для визуализации --- >>>
    VIS_DIMS = 512
    VIS_PARAMS_RGB = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000}
    # Используем только один канал B8, GEE вернет серое изображение
    VIS_PARAMS_NIR = {'bands': ['B8'], 'min': 0, 'max': 3000}

    def __init__(self, rgb_image_path: str = None, nir_image_path: str = None):
        self.rgb_image, self.red_channel, self.green_channel, self.blue_channel, self.nir_channel = None, None, None, None, None
        self.cloud_percentage = None
        if rgb_image_path: 
            self._load_local_images(rgb_image_path, nir_image_path)

    def _load_local_images(self, rgb_path, nir_path):
        img_bgr = cv2.imread(rgb_path)
        self.rgb_image = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        self.red_channel, self.green_channel, self.blue_channel = self.rgb_image[:, :, 0].astype(np.float32), \
        self.rgb_image[:, :, 1].astype(np.float32), self.rgb_image[:, :, 2].astype(np.float32)
        if nir_path: 
            self.nir_channel = cv2.imread(nir_path, cv2.IMREAD_GRAYSCALE).astype(np.float32)
            self._align_images()

    def _align_images(self):
        if self.rgb_image is not None and self.nir_channel is not None and self.rgb_image.shape[:2] != self.nir_channel.shape:
            h, w = self.rgb_image.shape[:2]
            self.nir_channel = cv2.resize(self.nir_channel, (w, h), interpolation=cv2.INTER_AREA)

    @staticmethod
    def _url_to_numpy(url: str) -> np.ndarray:
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            img_array = np.frombuffer(response.content, np.uint8)
            img_bgr = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img_bgr is None:
                raise ValueError("cv2.imdecode returned None. Image format may be unsupported or data is corrupt.")
            return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image from URL: {url}. Error: {e}")
        except Exception as e:
            print(f"Error processing image from URL: {url}. Error: {e}")
        return np.zeros((ImageProvider.VIS_DIMS, ImageProvider.VIS_DIMS, 3), dtype=np.uint8)

    @classmethod
    def _ensure_gee_initialized(cls, service_account_key_path: str = "hack25addcode-3171f61bba2c.json"):
        if not GEEInitializer.is_initialized():
            GEEInitializer.initialize_gee(service_account_key_path)

    @classmethod
    def get_images_from_gee_collection(cls, start_date: str, end_date: str,
                                       area_of_interest: ee.Geometry,
                                       service_account_key_path: str = "hack25addcode-3171f61bba2c.json") -> List[Dict]:
        cls._ensure_gee_initialized(service_account_key_path)

        collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                      .filterBounds(area_of_interest)
                      .filterDate(start_date, end_date)
                      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cls.CLOUD_FILTER_PERCENTAGE)))

        image_count = collection.size().getInfo()
        print(f"Найдено изображений в коллекции (с облачностью < {cls.CLOUD_FILTER_PERCENTAGE}%): {image_count}")
        if image_count == 0:
            raise FileNotFoundError(f"Не найдено снимков за указанный период с облачностью менее {cls.CLOUD_FILTER_PERCENTAGE}%. Попробуйте расширить диапазон дат.")

        def get_metadata(image):
            return ee.Feature(None, {
                'id': image.get('system:id'),
                'date': image.date().format('YYYY-MM-dd'),
                'cloud_percentage': image.get('CLOUDY_PIXEL_PERCENTAGE')
            })

        print("Получение списка снимков...")
        metadata_list = collection.map(get_metadata).getInfo()['features']

        processed_images = []
        stable_bounds = area_of_interest.bounds()

        for metadata in metadata_list:
            props = metadata['properties']
            image_id = props['id']
            date = props['date']
            cloud_percentage = props['cloud_percentage']
            
            print(f"Обработка снимка от {date} (облачность: {cloud_percentage:.2f}%)")
            
            try:
                image = ee.Image(image_id)
                clipped_image = image.clip(stable_bounds)

                # <<< --- КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: ЗАМЕНА sampleRectangle НА getThumbURL --- >>>
                # 1. Получаем RGB изображение для визуализации и каналов R, G, B
                rgb_params = {**cls.VIS_PARAMS_RGB, 'dimensions': cls.VIS_DIMS}
                rgb_url = clipped_image.getThumbURL(rgb_params)
                rgb_image = cls._url_to_numpy(rgb_url)

                # 2. Получаем NIR канал как отдельное серое изображение
                nir_params = {**cls.VIS_PARAMS_NIR, 'dimensions': cls.VIS_DIMS}
                nir_url = clipped_image.getThumbURL(nir_params)
                nir_image_gray = cls._url_to_numpy(nir_url)
                
                # 3. Извлекаем каналы из полученных изображений
                # GEE масштабирует значения каналов в диапазон 0-255 для getThumbURL.
                # Для вегетационных индексов, которые являются отношениями (ratio),
                # это не критично и дает корректный результат.
                red_channel = rgb_image[:, :, 0].astype(np.float32)
                green_channel = rgb_image[:, :, 1].astype(np.float32)
                blue_channel = rgb_image[:, :, 2].astype(np.float32)
                # Для серого изображения все каналы (R,G,B) одинаковы, берем любой
                nir_channel = nir_image_gray[:, :, 0].astype(np.float32)

                processed_images.append({
                    'date': date,
                    'cloud_percentage': cloud_percentage,
                    'rgb_image': rgb_image, # Это уже готовый numpy array
                    'red_channel': red_channel,
                    'green_channel': green_channel,
                    'blue_channel': blue_channel,
                    'nir_channel': nir_channel
                })
            except Exception as e:
                print(f"Ошибка при обработке снимка {image_id}: {e}. Пропускаем.")
        
        if not processed_images:
            raise FileNotFoundError("Не удалось обработать ни одного снимка. Возможно, все они содержат ошибки или пусты.")
            
        return processed_images

    @classmethod
    def from_gee(cls, start_date: str, end_date: str,
                 lon: float = None, lat: float = None, radius_km: float = 0.5,
                 polygon_coords: List[List[float]] = None,
                 service_account_key_path: str = "hack25addcode-3171f61bba2c.json"):
        cls._ensure_gee_initialized(service_account_key_path)

        if polygon_coords:
            if len(polygon_coords) < 3:
                raise ValueError("Для полигона необходимо как минимум 3 точки.")
<<<<<<< HEAD
            area_of_interest = ee.Geometry.Polygon([polygon_coords])
=======
            area_of_interest = ee.Geometry.Polygon(polygon_coords)
>>>>>>> parent of 7e7c5d1 (Add files via upload)
        elif lon is not None and lat is not None:
            point = ee.Geometry.Point([lon, lat])
            area_of_interest = point.buffer(radius_km * 1000).bounds()
        else:
            raise ValueError("Необходимо указать либо координаты точки (lon, lat) и радиус, либо координаты полигона.")

        collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                      .filterBounds(area_of_interest)
                      .filterDate(start_date, end_date)
                      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cls.CLOUD_FILTER_PERCENTAGE)))

        cleanest_image = ee.Image(collection.sort('CLOUDY_PIXEL_PERCENTAGE').first()).clip(area_of_interest.bounds())
        
        try:
            cloud_percentage = cleanest_image.get('CLOUDY_PIXEL_PERCENTAGE').getInfo()
        except ee.EEException as e:
            if 'dictionary is empty' in str(e).lower():
                 raise FileNotFoundError(f"Не найдено снимков за указанный период с облачностью менее {cls.CLOUD_FILTER_PERCENTAGE}%. Попробуйте расширить диапазон дат.")
            raise e

        print(f"Выбран самый чистый снимок с облачностью: {cloud_percentage:.2f}%")
        
        provider = cls()
        provider.cloud_percentage = cloud_percentage
        
        # <<< --- ИЗМЕНЕНИЕ: Аналогичная замена для этого метода --- >>>
        # 1. Получаем RGB
        rgb_params = {**cls.VIS_PARAMS_RGB, 'dimensions': cls.VIS_DIMS * 10} # *10 для лучшего качества одиночного снимка
        provider.rgb_image = cls._url_to_numpy(cleanest_image.getThumbURL(rgb_params))
        
        # 2. Получаем NIR
        nir_params = {**cls.VIS_PARAMS_NIR, 'dimensions': cls.VIS_DIMS * 10}
        nir_image_gray = cls._url_to_numpy(cleanest_image.getThumbURL(nir_params))
        
        # 3. Извлекаем каналы
        provider.red_channel = provider.rgb_image[:, :, 0].astype(np.float32)
        provider.green_channel = provider.rgb_image[:, :, 1].astype(np.float32)
        provider.blue_channel = provider.rgb_image[:, :, 2].astype(np.float32)
        provider.nir_channel = nir_image_gray[:, :, 0].astype(np.float32)
        
        print("Данные для одного снимка успешно загружены.")
        return provider

    @classmethod
    def get_historical_ndvi(cls, area_of_interest: ee.Geometry, start_date: str, end_date: str) -> List[Dict]:
        cls._ensure_gee_initialized()

        def calculate_monthly_mean(image_collection):
            years = ee.List.sequence(ee.Date(start_date).get('year'), ee.Date(end_date).get('year'))
            
            def process_year(year):
                def process_month(month):
                    start = ee.Date.fromYMD(year, month, 1)
                    end = start.advance(1, 'month')
                    monthly_collection = image_collection.filterDate(start, end)
                    cleanest_in_month = monthly_collection.sort('CLOUDY_PIXEL_PERCENTAGE').first()
                    
                    def compute_mean(img):
                        ndvi = img.normalizedDifference(['B8', 'B4']).rename('NDVI')
                        mean_dict = ndvi.reduceRegion(
                            reducer=ee.Reducer.mean(), 
                            geometry=area_of_interest, 
                            scale=30, # reduceRegion работает иначе, здесь scale обязателен и не вызывает ошибок
                            maxPixels=1e9
                        )
                        return ee.Feature(None, {
                            'date': start.format('YYYY-MM-dd'), 
                            'mean_ndvi': mean_dict.get('NDVI')
                        })
                    
                    return ee.Algorithms.If(cleanest_in_month, compute_mean(ee.Image(cleanest_in_month)), None)
                
                months = ee.List.sequence(1, 12)
                return months.map(process_month)
            
            monthly_data = years.map(process_year).flatten()
            return monthly_data.removeAll([None]).getInfo()

        collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                      .filterBounds(area_of_interest)
                      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cls.CLOUD_FILTER_PERCENTAGE)))
        historical_data = calculate_monthly_mean(collection)
        return historical_data
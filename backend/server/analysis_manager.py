# --- START OF FILE analysis_manager.py ---

import json
import time
import logging
from typing import Dict, List, Optional
from ImageProvider import ImageProvider
from index_calculator import VegetationIndexCalculator
from gee_initializer import GEEInitializer
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import ee
import cv2

logger = logging.getLogger(__name__)

class AnalysisManager:
    """
    Класс-оркестратор для выполнения анализа спутниковых снимков.
    Отвечает за получение данных, вычисление индексов, генерацию изображений
    и сохранение результатов в базу данных.
    """
    def __init__(self, db_manager):
        self.db = db_manager

    # --- Методы для работы с данными пользователя в БД ---

    def _get_user_data_object(self, token: str) -> dict:
        """Вспомогательная функция для получения и парсинга данных пользователя."""
        data_str = self.db.get_user_data(token)
        if data_str:
            try:
                data_obj = json.loads(data_str)
                if 'analyses' not in data_obj: data_obj['analyses'] = []
                if 'saved_fields' not in data_obj: data_obj['saved_fields'] = []
                return data_obj
            except json.JSONDecodeError:
                logger.warning(f"Не удалось распарсить JSON для токена {token}. Возвращаем пустую структуру.")
                return {'analyses': [], 'saved_fields': []}
        return {'analyses': [], 'saved_fields': []}

    def _save_user_data_object(self, token: str, data_obj: dict) -> bool:
        """Вспомогательная функция для сохранения объекта данных пользователя."""
        try:
            data_str = json.dumps(data_obj)
            return self.db.save_user_data(token, data_str)
        except Exception as e:
            logger.error(f"Ошибка при сериализации и сохранении данных для токена {token}: {e}")
            return False

    # --- Методы для вычислений и обработки ---

    def _calculate_zones(self, index_map: np.ndarray, thresholds: Dict[str, List[float]]) -> Dict:
        """Разделяет карту индекса на зоны и вычисляет их процентное соотношение."""
        total_pixels = np.count_nonzero(~np.isnan(index_map))
        if total_pixels == 0:
            return {'low': 0, 'medium': 0, 'high': 0}
            
        zones = {}
        for zone_name, (lower, upper) in thresholds.items():
            mask = (index_map >= lower) & (index_map < upper)
            pixel_count = np.count_nonzero(mask)
            zones[zone_name] = round((pixel_count / total_pixels) * 100, 2)
            
        return zones

    def _calculate_all_indices(self, calculator: VegetationIndexCalculator) -> Dict:
        """Вычисляет все вегетационные индексы и их статистику на основе калькулятора."""
        indices_data = {}
        
        # NDVI
        ndvi_map = calculator.calculate_ndvi()
        ndvi_stats = {'min': float(np.nanmin(ndvi_map)), 'max': float(np.nanmax(ndvi_map)), 'mean': float(np.nanmean(ndvi_map)), 'std': float(np.nanstd(ndvi_map))}
        ndvi_zones = self._calculate_zones(ndvi_map, {'low': [-1, 0.2], 'medium': [0.2, 0.5], 'high': [0.5, 1.01]})
        indices_data['ndvi'] = {'map': ndvi_map, 'stats': ndvi_stats, 'zones': ndvi_zones}
        
        # SAVI
        savi_map = calculator.calculate_savi()
        savi_stats = {'min': float(np.nanmin(savi_map)), 'max': float(np.nanmax(savi_map)), 'mean': float(np.nanmean(savi_map)), 'std': float(np.nanstd(savi_map))}
        indices_data['savi'] = {'map': savi_map, 'stats': savi_stats}

        # VARI
        vari_map = calculator.calculate_vari()
        vari_stats = {'min': float(np.nanmin(vari_map)), 'max': float(np.nanmax(vari_map)), 'mean': float(np.nanmean(vari_map)), 'std': float(np.nanstd(vari_map))}
        indices_data['vari'] = {'map': vari_map, 'stats': vari_stats}
        
        # EVI
        evi_map = calculator.calculate_evi()
        evi_stats = {'min': float(np.nanmin(evi_map)), 'max': float(np.nanmax(evi_map)), 'mean': float(np.nanmean(evi_map)), 'std': float(np.nanstd(evi_map))}
        indices_data['evi'] = {'map': evi_map, 'stats': evi_stats}
        
        return indices_data
    
    # --- Методы для генерации изображений ---

    def _array_to_base64(self, array: np.ndarray) -> str:
        """Конвертирует numpy array (карту индекса) в серую base64 строку для отчета."""
        try:
            array_min = np.nanmin(array)
            array_max = np.nanmax(array)
            if array_max > array_min:
                normalized = (255 * (array - array_min) / (array_max - array_min))
            else:
                normalized = np.zeros_like(array)

            normalized[np.isnan(normalized)] = 0
            normalized = normalized.astype(np.uint8)
                
            image = Image.fromarray(normalized, mode='L').convert('RGB')
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode()
        except Exception as e:
            logger.error(f"Ошибка конвертации массива в base64: {e}")
            return ""

    # <<< --- НОВЫЙ МЕТОД ДЛЯ RGB --- >>>
    def _rgb_array_to_base64(self, rgb_array: np.ndarray) -> str:
        """Конвертирует цветной RGB numpy array в base64 строку."""
        try:
            image = Image.fromarray(rgb_array.astype(np.uint8), mode='RGB')
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode()
        except Exception as e:
            logger.error(f"Ошибка конвертации RGB массива в base64: {e}")
            return ""

    def _colorize_ndvi(self, ndvi_map: np.ndarray) -> str:
        """
        Принимает карту NDVI (значения от -1 до 1) и возвращает
        цветное PNG изображение в формате base64 с альфа-каналом для оверлея.
        """
        try:
            ndvi_map_clipped = np.clip(ndvi_map, 0, 1)
            normalized = (ndvi_map_clipped * 255).astype(np.uint8)
            mask_nan = np.isnan(ndvi_map)

            # Создаем кастомную цветовую карту Red -> Yellow -> Green
            lut = np.zeros((256, 1, 3), dtype=np.uint8)
            for i in range(256):
                if i < 128:
                    lut[i, 0, 0] = 0 # Blue
                    lut[i, 0, 1] = i * 2 # Green
                    lut[i, 0, 2] = 255 # Red
                else:
                    lut[i, 0, 0] = 0 # Blue
                    lut[i, 0, 1] = 255 # Green
                    lut[i, 0, 2] = 255 - (i - 128) * 2 # Red
            
            colored_bgr = cv2.LUT(cv2.cvtColor(normalized, cv2.COLOR_GRAY2BGR), lut)
            bgra = cv2.cvtColor(colored_bgr, cv2.COLOR_BGR2BGRA)

            # Устанавливаем прозрачность для NaN значений
            bgra[:, :, 3] = 255
            bgra[mask_nan, 3] = 0

            _, buffer = cv2.imencode('.png', bgra)
            return base64.b64encode(buffer).decode('utf-8')

        except Exception as e:
            logger.error(f"Ошибка при раскрашивании NDVI: {e}")
            return ""

    # <<< --- ИЗМЕНЕННЫЙ МЕТОД --- >>>
    def _create_problem_zones_image(self, rgb_image: np.ndarray, ndvi_map: np.ndarray, threshold: float = 0.2) -> str:
        """
        Подсвечивает проблемные зоны (NDVI < threshold) красным цветом
        на сером фоне оригинального снимка для отчета.
        """
        try:
            # Получаем целевые размеры из RGB-изображения
            h, w = rgb_image.shape[:2]

            # Изменяем размер карты NDVI, чтобы он соответствовал RGB-изображению
            # Используем INTER_NEAREST, чтобы избежать создания новых значений NDVI при интерполяции
            resized_ndvi_map = cv2.resize(ndvi_map, (w, h), interpolation=cv2.INTER_NEAREST)

            problem_mask = (resized_ndvi_map < threshold) & (~np.isnan(resized_ndvi_map))
            bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
            gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
            gray_bgr = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)

            red_layer = np.zeros_like(gray_bgr)
            red_layer[:, :] = [0, 0, 255] # BGR -> Red

            output_image = gray_bgr.copy()
            if np.any(problem_mask):
                # Накладываем красный цвет с 40% прозрачностью
                blended = cv2.addWeighted(gray_bgr[problem_mask], 0.6, red_layer[problem_mask], 0.4, 0)
                output_image[problem_mask] = blended

            _, buffer = cv2.imencode('.jpg', output_image)
            return base64.b64encode(buffer).decode('utf-8')

        except Exception as e:
            logger.error(f"Ошибка при создании карты проблемных зон: {e}")
            return ""


    # --- Методы для работы с полными данными анализа ---

    def _save_analysis_data(self, token: str, analysis_id: str, analysis_data: Dict) -> bool:
        """Сохраняет ПОЛНЫЕ данные анализа (включая изображения) в базу данных."""
        try:
            analysis_data_serialized = json.dumps(analysis_data, default=str)
            return self.db.save_analysis_data(token, analysis_id, analysis_data_serialized)
        except Exception as e:
            logger.error(f"Ошибка сохранения анализа: {e}")
            return False
    
    def _load_analysis_data(self, token: str, analysis_id: str) -> Optional[Dict]:
        """Загружает данные анализа из базы данных."""
        try:
            data = self.db.get_analysis_data(token, analysis_id)
            if data: return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Ошибка загрузки анализа: {e}")
            return None
    
    # --- Основной публичный метод ---

    def perform_complete_analysis(self, token: str, start_date: str, end_date: str, 
                                lon: Optional[float] = None, lat: Optional[float] = None, 
                                radius_km: float = 0.5, 
                                polygon_coords: Optional[List[List[float]]] = None) -> Dict:
        """
        Выполняет полный цикл анализа: получает снимки, рассчитывает индексы,
        генерирует все необходимые изображения и сохраняет результат.
        """
        try:
            GEEInitializer.initialize_gee()
            
            area_info = {}
            area_of_interest = None
            if polygon_coords:
                area_info = {'type': 'polygon', 'coordinates': polygon_coords}
                area_of_interest = ee.Geometry.Polygon(polygon_coords)
                logger.info(f"Запуск анализа коллекции для полигона...")
            elif lon is not None and lat is not None:
                area_info = {'type': 'point_radius', 'lon': lon, 'lat': lat, 'radius_km': radius_km}
                point = ee.Geometry.Point([lon, lat])
                area_of_interest = point.buffer(radius_km * 1000)
                logger.info(f"Запуск анализа коллекции для: {lon}, {lat} с радиусом {radius_km} км")
            else:
                raise ValueError("Не указана область для анализа (ни точка с радиусом, ни полигон).")

            bounds_coords_list = area_of_interest.bounds().coordinates().get(0).getInfo()
            bounds_for_leaflet = [[bounds_coords_list[0][1], bounds_coords_list[0][0]], [bounds_coords_list[2][1], bounds_coords_list[2][0]]]

            image_data_list = ImageProvider.get_images_from_gee_collection(
                start_date=start_date, end_date=end_date,
                area_of_interest=area_of_interest
            )
            
            all_results = []
            
            for image_data in image_data_list:
                calculator = VegetationIndexCalculator(
                    rgb_image=image_data['rgb_image'], red_channel=image_data['red_channel'],
                    green_channel=image_data['green_channel'], blue_channel=image_data['blue_channel'],
                    nir_channel=image_data['nir_channel']
                )
                
                indices = self._calculate_all_indices(calculator)
                
                colored_ndvi_base64 = self._colorize_ndvi(indices['ndvi']['map'])
                problem_zones_base64 = self._create_problem_zones_image(
                    rgb_image=image_data['rgb_image'],
                    ndvi_map=indices['ndvi']['map']
                )
                
                single_image_result = {
                    'date': image_data['date'],
                    'cloud_coverage': image_data['cloud_percentage'],
                    'images': {
                        # <<< --- ИЗМЕНЕНИЕ: Используем правильную функцию для RGB --- >>>
                        'rgb': self._rgb_array_to_base64(image_data['rgb_image']),
                        'ndvi': self._array_to_base64(indices['ndvi']['map']),
                        'savi': self._array_to_base64(indices['savi']['map']),
                        'vari': self._array_to_base64(indices['vari']['map']),
                        'evi': self._array_to_base64(indices['evi']['map'])
                    },
                    'ndvi_overlay_image': colored_ndvi_base64,
                    'problem_zones_image': problem_zones_base64,
                    'bounds': bounds_for_leaflet,
                    'statistics': {
                        'ndvi': indices['ndvi']['stats'],
                        'savi': indices['savi']['stats'],
                        'vari': indices['vari']['stats'],
                        'evi': indices['evi']['stats']
                    },
                    'zoning': {
                        'ndvi': indices['ndvi']['zones']
                    }
                }
                all_results.append(single_image_result)

            analysis_id = str(int(time.time()))
            all_results.sort(key=lambda x: x['date'])
            analysis_data_response = {
                'analysis_id': analysis_id,
                'timestamp': time.time(),
                'area_of_interest': area_info,
                'date_range': {'start': start_date, 'end': end_date},
                'image_count': len(all_results),
                'results_per_image': all_results,
                'metadata': { 'resolution': '10m', 'source': 'Sentinel-2' }
            }
            
            if self._save_analysis_data(token, analysis_id, analysis_data_response):
                self._update_user_analyses_list(token, analysis_id, analysis_data_response)
                logger.info(f"Анализ коллекции {analysis_id} успешно сохранен")
                return {'status': 'success', 'analysis_id': analysis_id, 'data': analysis_data_response}
            else:
                raise Exception("Не удалось сохранить анализ")
                
        except Exception as e:
            logger.error(f"Ошибка при выполнении анализа коллекции: {e}")
            return {'status': 'error', 'detail': str(e)}
    
    def _update_user_analyses_list(self, token: str, analysis_id: str, analysis_data: Dict):
        """Обновляет список анализов пользователя с краткой сводкой."""
        try:
            user_data_obj = self._get_user_data_object(token)
            
            avg_ndvi, avg_vari, avg_evi = 0, 0, 0
            if analysis_data.get('image_count', 0) > 0:
                ndvis = [r['statistics']['ndvi']['mean'] for r in analysis_data['results_per_image']]
                varis = [r['statistics']['vari']['mean'] for r in analysis_data['results_per_image']]
                evis = [r['statistics']['evi']['mean'] for r in analysis_data['results_per_image']]
                avg_ndvi = sum(ndvis) / len(ndvis) if ndvis else 0
                avg_vari = sum(varis) / len(varis) if varis else 0
                avg_evi = sum(evis) / len(evis) if evis else 0

            new_analysis = {
                'analysis_id': analysis_id,
                'timestamp': analysis_data['timestamp'],
                'area_of_interest': analysis_data['area_of_interest'],
                'date_range': analysis_data['date_range'],
                'image_count': analysis_data.get('image_count', 0),
                'statistics_summary': {
                    'ndvi_mean': avg_ndvi,
                    'vari_mean': avg_vari,
                    'evi_mean': avg_evi
                }
            }
            
            user_data_obj['analyses'].insert(0, new_analysis)
            user_data_obj['analyses'] = user_data_obj['analyses'][:50]
            
            self._save_user_data_object(token, user_data_obj)
            
        except Exception as e:
            logger.error(f"Ошибка обновления списка анализов: {e}")
    
    # --- CRUD-методы для управления анализами ---

    def get_analysis_by_id(self, token: str, analysis_id: str) -> Dict:
        """Получает конкретный анализ по ID."""
        try:
            analysis_data = self._load_analysis_data(token, analysis_id)
            if analysis_data:
                return {'status': 'success', 'analysis_id': analysis_id, 'data': analysis_data}
            else:
                return {'status': 'error', 'detail': 'Анализ не найден'}
        except Exception as e:
            logger.error(f"Ошибка получения анализа: {e}")
            return {'status': 'error', 'detail': str(e)}
    
    def delete_analysis(self, token: str, analysis_id: str) -> Dict:
        """Удаляет анализ из основной БД и из списка пользователя."""
        try:
            self.db.delete_analysis_data(token, analysis_id)
            
            user_data_obj = self._get_user_data_object(token)
            initial_count = len(user_data_obj.get('analyses', []))
            
            user_data_obj['analyses'] = [
                analysis for analysis in user_data_obj.get('analyses', []) 
                if analysis.get('analysis_id') != analysis_id
            ]
            
            if len(user_data_obj['analyses']) < initial_count:
                self._save_user_data_object(token, user_data_obj)
                logger.info(f"Анализ {analysis_id} удален из списка пользователя {token}")
                return {'status': 'success', 'message': 'Анализ успешно удален'}
            else:
                logger.warning(f"Анализ {analysis_id} не был найден в списке пользователя {token} для удаления.")
                return {'status': 'success', 'message': 'Анализ успешно удален'}
                
        except Exception as e:
            logger.error(f"Критическая ошибка при удалении анализа {analysis_id}: {e}")
            return {'status': 'error', 'detail': str(e)}
# --- START OF FILE analysis_manager.py ---

import json
import time
import logging
from typing import Dict, List, Optional
from ImageProvider import ImageProvider
from index_calculator import VegetationIndexCalculator
from gee_initializer import GEEInitializer  # Добавляем импорт
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import ee

logger = logging.getLogger(__name__)

class AnalysisManager:
    def __init__(self, db_manager):
        self.db = db_manager

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
            
    def _calculate_zones(self, index_map: np.ndarray, thresholds: Dict[str, List[float]]) -> Dict:
        """Разделяет карту индекса на зоны и вычисляет их процентное соотношение."""
        total_pixels = index_map.size
        if total_pixels == 0:
            return {}
            
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
        
        return indices_data
    
    def _array_to_base64(self, array: np.ndarray) -> str:
        """Конвертирует numpy array в base64 строку"""
        try:
            if array.dtype != np.uint8:
                array_min = np.nanmin(array)
                array_max = np.nanmax(array)
                if array_max > array_min:
                    normalized = (255 * (array - array_min) / (array_max - array_min)).astype(np.uint8)
                else:
                    normalized = np.zeros_like(array, dtype=np.uint8)
            else:
                normalized = array
                
            if len(array.shape) == 2:
                image = Image.fromarray(normalized, mode='L').convert('RGB')
            else:
                image = Image.fromarray(normalized)
                
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode()
        except Exception as e:
            logger.error(f"Ошибка конвертации массива в base64: {e}")
            return ""
    
    def _save_analysis_data(self, token: str, analysis_id: str, analysis_data: Dict) -> bool:
        """
        Сохраняет ПОЛНЫЕ данные анализа (включая изображения) в базу данных.
        """
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
    
    def perform_complete_analysis(self, token: str, start_date: str, end_date: str, 
                                lon: Optional[float] = None, lat: Optional[float] = None, 
                                radius_km: float = 0.5, 
                                polygon_coords: Optional[List[List[float]]] = None) -> Dict:
        """
        Выполняет анализ ВСЕХ снимков за период и сохраняет агрегированный результат.
        """
        try:
            # Гарантируем инициализацию GEE перед использованием
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
                area_of_interest = point.buffer(radius_km * 1000).bounds()
                logger.info(f"Запуск анализа коллекции для: {lon}, {lat} с радиусом {radius_km} км")
            else:
                raise ValueError("Не указана область для анализа (ни точка с радиусом, ни полигон).")

            # Шаг 1: Получаем все данные по всем снимкам
            image_data_list = ImageProvider.get_images_from_gee_collection(
                start_date=start_date, end_date=end_date,
                area_of_interest=area_of_interest
            )
            
            all_results = []
            
            # Шаг 2: Обрабатываем каждый снимок
            for image_data in image_data_list:
                calculator = VegetationIndexCalculator(
                    rgb_image=image_data['rgb_image'],
                    red_channel=image_data['red_channel'],
                    green_channel=image_data['green_channel'],
                    blue_channel=image_data['blue_channel'],
                    nir_channel=image_data['nir_channel']
                )
                
                indices = self._calculate_all_indices(calculator)
                
                single_image_result = {
                    'date': image_data['date'],
                    'cloud_coverage': image_data['cloud_percentage'],
                    'images': {
                        'rgb': self._array_to_base64(image_data['rgb_image']),
                        'ndvi': self._array_to_base64(indices['ndvi']['map']),
                        'savi': self._array_to_base64(indices['savi']['map']),
                        'vari': self._array_to_base64(indices['vari']['map'])
                    },
                    'statistics': {
                        'ndvi': indices['ndvi']['stats'],
                        'savi': indices['savi']['stats'],
                        'vari': indices['vari']['stats']
                    },
                    'zoning': {
                        'ndvi': indices['ndvi']['zones']
                    }
                }
                all_results.append(single_image_result)

            # Шаг 3: Собираем финальный ответ
            analysis_id = str(int(time.time()))
            
            all_results.sort(key=lambda x: x['date'])
            
            analysis_data_response = {
                'analysis_id': analysis_id,
                'timestamp': time.time(),
                'area_of_interest': area_info,
                'date_range': {'start': start_date, 'end': end_date},
                'image_count': len(all_results),
                'results_per_image': all_results,
                'metadata': {
                    'resolution': '10m',
                    'source': 'Sentinel-2'
                }
            }
            
            # Шаг 4: Сохраняем результат
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
        """Обновляет список анализов пользователя"""
        try:
            user_data_obj = self._get_user_data_object(token)
            
            avg_ndvi = 0
            avg_vari = 0
            if analysis_data.get('image_count', 0) > 0:
                ndvis = [r['statistics']['ndvi']['mean'] for r in analysis_data['results_per_image']]
                varis = [r['statistics']['vari']['mean'] for r in analysis_data['results_per_image']]
                avg_ndvi = sum(ndvis) / len(ndvis) if ndvis else 0
                avg_vari = sum(varis) / len(varis) if varis else 0

            new_analysis = {
                'analysis_id': analysis_id,
                'timestamp': analysis_data['timestamp'],
                'area_of_interest': analysis_data['area_of_interest'],
                'date_range': analysis_data['date_range'],
                'image_count': analysis_data.get('image_count', 0),
                'statistics_summary': {
                    'ndvi_mean': avg_ndvi,
                    'vari_mean': avg_vari
                }
            }
            
            user_data_obj['analyses'].insert(0, new_analysis)
            user_data_obj['analyses'] = user_data_obj['analyses'][:50]
            
            self._save_user_data_object(token, user_data_obj)
            
        except Exception as e:
            logger.error(f"Ошибка обновления списка анализов: {e}")
    
    def get_analysis_by_id(self, token: str, analysis_id: str) -> Dict:
        """Получает конкретный анализ по ID"""
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
        """Удаляет анализ"""
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
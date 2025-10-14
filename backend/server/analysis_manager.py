import json
import time
import logging
from typing import Dict, List, Optional
from ImageProvider import ImageProvider
from index_calculator import VegetationIndexCalculator
import numpy as np
import base64
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)

class AnalysisManager:
    def __init__(self, user_data_db, field_data_db):
        self.user_data = user_data_db
        self.field_data = field_data_db

    def _get_user_data_object(self, token: str) -> dict:
        """Вспомогательная функция для получения и парсинга данных пользователя."""
        data_str = self.user_data.get_user_data(token)
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
            return self.user_data.save_user_data(token, data_str)
        except Exception as e:
            logger.error(f"Ошибка при сериализации и сохранении данных для токена {token}: {e}")
            return False
            
    # --- НОВЫЙ МЕТОД ---
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

    # --- ИЗМЕНЕННЫЙ МЕТОД ---
    def _calculate_all_indices(self, provider: ImageProvider) -> Dict:
        """Вычисляет все вегетационные индексы и их статистику."""
        calculator = VegetationIndexCalculator(
            rgb_image=provider.rgb_image,
            red_channel=provider.red_channel,
            green_channel=provider.green_channel,
            blue_channel=provider.blue_channel,
            nir_channel=provider.nir_channel
        )
        
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
        """Сохраняет данные анализа в поле"""
        try:
            analysis_data_for_storage = analysis_data.copy()
            if 'images' in analysis_data_for_storage:
                del analysis_data_for_storage['images']
            
            analysis_data_serialized = json.dumps(analysis_data_for_storage, default=str)
            field_name = f"analysis_{token}_{analysis_id}"
            return self.field_data.edit_field_data(field_name, analysis_data_serialized)
        except Exception as e:
            logger.error(f"Ошибка сохранения анализа: {e}")
            return False
    
    def _load_analysis_data(self, token: str, analysis_id: str) -> Optional[Dict]:
        """Загружает данные анализа из поля"""
        try:
            field_name = f"analysis_{token}_{analysis_id}"
            data = self.field_data.get_field_data(field_name)
            if data: return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Ошибка загрузки анализа: {e}")
            return None
    
    # --- ИЗМЕНЕННЫЙ МЕТОД ---
    def perform_complete_analysis(self, token: str, start_date: str, end_date: str, 
                                lon: Optional[float] = None, lat: Optional[float] = None, 
                                radius_km: float = 0.5, 
                                polygon_coords: Optional[List[List[float]]] = None) -> Dict:
        """Выполняет полный анализ и сохраняет результаты"""
        try:
            area_info = {}
            if polygon_coords:
                area_info = {'type': 'polygon', 'coordinates': polygon_coords}
                logger.info(f"Запуск полного анализа для полигона...")
            elif lon is not None and lat is not None:
                area_info = {'type': 'point_radius', 'lon': lon, 'lat': lat, 'radius_km': radius_km}
                logger.info(f"Запуск полного анализа для координат: {lon}, {lat} с радиусом {radius_km} км")
            else:
                raise ValueError("Не указана область для анализа (ни точка с радиусом, ни полигон).")

            provider = ImageProvider.from_gee(
                start_date=start_date, end_date=end_date,
                lon=lon, lat=lat, radius_km=radius_km,
                polygon_coords=polygon_coords
            )
            
            indices = self._calculate_all_indices(provider)
            
            analysis_id = str(int(time.time()))
            analysis_data = {
                'analysis_id': analysis_id,
                'timestamp': time.time(),
                'area_of_interest': area_info,
                'date_range': {'start': start_date, 'end': end_date},
                'images': {
                    'rgb': self._array_to_base64(provider.rgb_image),
                    'ndvi': self._array_to_base64(indices['ndvi']['map']),
                    'savi': self._array_to_base64(indices['savi']['map']),
                    'vari': self._array_to_base64(indices['vari']['map'])
                },
                'statistics': {
                    'ndvi': indices['ndvi']['stats'],
                    'savi': indices['savi']['stats'],
                    'vari': indices['vari']['stats']
                },
                'zoning': { # Добавлено
                    'ndvi': indices['ndvi']['zones']
                },
                'metadata': { # Добавлено
                    'cloud_coverage': provider.cloud_percentage if hasattr(provider, 'cloud_percentage') else 'unknown',
                    'resolution': '10m',
                    'source': 'Sentinel-2'
                }
            }
            
            if self._save_analysis_data(token, analysis_id, analysis_data):
                self._update_user_analyses_list(token, analysis_id, analysis_data)
                logger.info(f"Анализ {analysis_id} успешно сохранен")
                return {'status': 'success', 'analysis_id': analysis_id, 'data': analysis_data}
            else:
                raise Exception("Не удалось сохранить анализ")
                
        except Exception as e:
            logger.error(f"Ошибка при выполнении анализа: {e}")
            return {'status': 'error', 'detail': str(e)}
    
    def _update_user_analyses_list(self, token: str, analysis_id: str, analysis_data: Dict):
        """Обновляет список анализов пользователя"""
        try:
            user_data_obj = self._get_user_data_object(token)
            
            new_analysis = {
                'analysis_id': analysis_id,
                'timestamp': analysis_data['timestamp'],
                'area_of_interest': analysis_data['area_of_interest'],
                'date_range': analysis_data['date_range'],
                'statistics_summary': {
                    'ndvi_mean': analysis_data['statistics']['ndvi']['mean'],
                    'vari_mean': analysis_data['statistics']['vari']['mean']
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
            field_name = f"analysis_{token}_{analysis_id}"
            self.field_data.delete_field_data(field_name)
            
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
                return {'status': 'error', 'detail': 'Анализ не найден в списке для удаления'}
                
        except Exception as e:
            logger.error(f"Критическая ошибка при удалении анализа {analysis_id}: {e}")
            return {'status': 'error', 'detail': str(e)}
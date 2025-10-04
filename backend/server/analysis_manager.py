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
    
    def _calculate_all_indices(self, provider: ImageProvider) -> Dict:
        """Вычисляет все вегетационные индексы"""
        calculator = VegetationIndexCalculator(
            rgb_image=provider.rgb_image,
            red_channel=provider.red_channel,
            green_channel=provider.green_channel,
            blue_channel=provider.blue_channel,
            nir_channel=provider.nir_channel
        )
        
        # Вычисляем индексы
        vari_map = calculator.calculate_vari()
        ndvi_map = calculator.calculate_ndvi()
        
        # Статистика по индексам
        vari_stats = {
            'min': float(vari_map.min()),
            'max': float(vari_map.max()),
            'mean': float(vari_map.mean()),
            'std': float(vari_map.std())
        }
        
        ndvi_stats = {
            'min': float(ndvi_map.min()),
            'max': float(ndvi_map.max()),
            'mean': float(ndvi_map.mean()),
            'std': float(ndvi_map.std())
        }
        
        return {
            'vari': {
                'map': vari_map,
                'stats': vari_stats
            },
            'ndvi': {
                'map': ndvi_map,
                'stats': ndvi_stats
            }
        }
    
    def _array_to_base64(self, array: np.ndarray) -> str:
        """Конвертирует numpy array в base64 строку"""
        try:
            # Нормализуем для визуализации
            if array.dtype != np.uint8:
                array_min = array.min()
                array_max = array.max()
                if array_max - array_min > 0:
                    normalized = ((array - array_min) / (array_max - array_min) * 255).astype(np.uint8)
                else:
                    normalized = np.zeros_like(array, dtype=np.uint8)
            else:
                normalized = array
                
            # Для одноканальных изображений
            if len(array.shape) == 2:
                image = Image.fromarray(normalized, mode='L')
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
            # Убираем большие массивы данных перед сохранением
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
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Ошибка загрузки анализа: {e}")
            return None
    
    def perform_complete_analysis(self, token: str, lon: float, lat: float, 
                                start_date: str, end_date: str) -> Dict:
        """Выполняет полный анализ и сохраняет результаты"""
        try:
            logger.info(f"Запуск полного анализа для координат: {lon}, {lat}")
            
            # Получаем данные изображения
            provider = ImageProvider.from_gee(
                lon=lon, lat=lat, 
                start_date=start_date, end_date=end_date
            )
            
            # Вычисляем индексы
            indices = self._calculate_all_indices(provider)
            
            # Создаем анализ
            analysis_id = str(int(time.time()))
            analysis_data = {
                'analysis_id': analysis_id,
                'timestamp': time.time(),
                'coordinates': {'lon': lon, 'lat': lat},
                'date_range': {'start': start_date, 'end': end_date},
                'images': {
                    'rgb': self._array_to_base64(provider.rgb_image),
                    'red_channel': self._array_to_base64(provider.red_channel),
                    'ndvi': self._array_to_base64(indices['ndvi']['map']),
                    'vari': self._array_to_base64(indices['vari']['map'])
                },
                'statistics': {
                    'red_channel': {
                        'min': float(provider.red_channel.min()),
                        'max': float(provider.red_channel.max()),
                        'mean': float(provider.red_channel.mean())
                    },
                    'ndvi': indices['ndvi']['stats'],
                    'vari': indices['vari']['stats']
                },
                'metadata': {
                    'cloud_coverage': 'unknown',
                    'resolution': '10m',
                    'source': 'Sentinel-2'
                }
            }
            
            # Сохраняем анализ
            if self._save_analysis_data(token, analysis_id, analysis_data):
                # Обновляем список анализов пользователя
                self._update_user_analyses_list(token, analysis_id, analysis_data)
                
                logger.info(f"Анализ {analysis_id} успешно сохранен")
                return {
                    'status': 'success',
                    'analysis_id': analysis_id,
                    'data': analysis_data
                }
            else:
                raise Exception("Не удалось сохранить анализ")
                
        except Exception as e:
            logger.error(f"Ошибка при выполнении анализа: {e}")
            return {
                'status': 'error',
                'detail': str(e)
            }
    
    def _update_user_analyses_list(self, token: str, analysis_id: str, analysis_data: Dict):
        """Обновляет список анализов пользователя"""
        try:
            # Получаем текущий список анализов
            analyses_list = self.get_user_analyses_list(token)
            
            # Добавляем новый анализ
            new_analysis = {
                'analysis_id': analysis_id,
                'timestamp': analysis_data['timestamp'],
                'coordinates': analysis_data['coordinates'],
                'date_range': analysis_data['date_range'],
                'statistics_summary': {
                    'ndvi_mean': analysis_data['statistics']['ndvi']['mean'],
                    'vari_mean': analysis_data['statistics']['vari']['mean']
                }
            }
            
            # Добавляем в начало и ограничиваем количество (например, последние 50 анализов)
            analyses_list['analyses'].insert(0, new_analysis)
            analyses_list['analyses'] = analyses_list['analyses'][:50]
            
            # Сохраняем обновленный список
            analyses_list_serialized = json.dumps(analyses_list)
            self.user_data.save_user_data(token, analyses_list_serialized)
            
        except Exception as e:
            logger.error(f"Ошибка обновления списка анализов: {e}")
    
    def get_user_analyses_list(self, token: str) -> Dict:
        """Получает список всех анализов пользователя"""
        try:
            data = self.user_data.get_user_data(token)
            if data:
                return json.loads(data)
            else:
                # Возвращаем пустой список, если данных нет
                return {'analyses': []}
        except Exception as e:
            logger.error(f"Ошибка получения списка анализов: {e}")
            return {'analyses': []}
    
    def get_analysis_by_id(self, token: str, analysis_id: str) -> Dict:
        """Получает конкретный анализ по ID"""
        try:
            analysis_data = self._load_analysis_data(token, analysis_id)
            if analysis_data:
                return {
                    'status': 'success',
                    'analysis_id': analysis_id,
                    'data': analysis_data
                }
            else:
                return {
                    'status': 'error',
                    'detail': 'Анализ не найден'
                }
        except Exception as e:
            logger.error(f"Ошибка получения анализа: {e}")
            return {
                'status': 'error',
                'detail': str(e)
            }
    
    def delete_analysis(self, token: str, analysis_id: str) -> Dict:
        """Удаляет анализ"""
        try:
            field_name = f"analysis_{token}_{analysis_id}"
            success = self.field_data.delete_field_data(field_name)
            
            if success:
                # Обновляем список анализов
                analyses_list = self.get_user_analyses_list(token)
                analyses_list['analyses'] = [
                    analysis for analysis in analyses_list['analyses'] 
                    if analysis['analysis_id'] != analysis_id
                ]
                
                # Сохраняем обновленный список
                analyses_list_serialized = json.dumps(analyses_list)
                self.user_data.save_user_data(token, analyses_list_serialized)
                
                return {
                    'status': 'success',
                    'message': 'Анализ удален'
                }
            else:
                return {
                    'status': 'error',
                    'detail': 'Не удалось удалить анализ'
                }
                
        except Exception as e:
            logger.error(f"Ошибка удаления анализа: {e}")
            return {
                'status': 'error',
                'detail': str(e)
            }
# --- START OF FILE gee_initializer.py ---

import os
import json
import ee
import logging

logger = logging.getLogger(__name__)

class GEEInitializer:
    _initialized = False
    
    @classmethod
    def initialize_gee(cls, service_account_key_path: str = "hack25addcode-3171f61bba2c.json"):
        """
        Инициализирует Google Earth Engine. Гарантирует однократную инициализацию.
        """
        if cls._initialized:
            logger.debug("GEE уже инициализирован")
            return True
            
        try:
            if service_account_key_path and os.path.exists(service_account_key_path):
                logger.info(f"Инициализация GEE с сервисным аккаунтом: {service_account_key_path}")
                with open(service_account_key_path) as f:
                    credentials_info = json.load(f)
                service_account_email = credentials_info['client_email']
                credentials = ee.ServiceAccountCredentials(service_account_email, service_account_key_path)
                ee.Initialize(credentials=credentials)
            else:
                logger.info("Инициализация GEE с учетными данными по умолчанию")
                ee.Initialize()
            
            cls._initialized = True
            logger.info("GEE успешно инициализирован")
            return True
            
        except ee.EEException as e:
            if 'already been initialized' in str(e).lower():
                cls._initialized = True
                logger.info("GEE уже был инициализирован ранее")
                return True
            else:
                logger.error(f"Ошибка инициализации Earth Engine: {e}")
                raise ConnectionError(f"Ошибка инициализации Earth Engine: {e}")
        except Exception as e:
            logger.error(f"Неожиданная ошибка при инициализации Earth Engine: {e}")
            raise ConnectionError(f"Неожиданная ошибка при инициализации Earth Engine: {e}")
    
    @classmethod
    def is_initialized(cls):
        """Проверяет, инициализирован ли GEE"""
        return cls._initialized
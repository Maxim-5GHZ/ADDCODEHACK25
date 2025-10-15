# --- START OF FILE gigachat_service.py ---
# --- START OF NEW FILE gigachat_service.py ---
import json
import logging
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

logger = logging.getLogger(__name__)

class GigaChatService:
    def __init__(self, config_path="config.json"):
        self.api_key = self._load_api_key(config_path)
        if not self.api_key:
            logger.error("Ключ API GigaChat не найден в config.json. Рекомендации AI не будут работать.")
            self.giga = None
        else:
            # verify_ssl_certs=False может понадобиться в некоторых окружениях
            self.giga = GigaChat(credentials=self.api_key, verify_ssl_certs=False)

    def _load_api_key(self, config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get("GIGACHAT_API_KEY")
        except FileNotFoundError:
            logger.warning(f"Файл конфигурации {config_path} не найден.")
            return None
        except json.JSONDecodeError:
            logger.error(f"Ошибка парсинга файла {config_path}.")
            return None

    # <<< --- НАЧАЛО ИЗМЕНЕНИЙ --- >>>
    async def get_recommendations(self, index_stats: dict) -> str:
        """
        Получает агрономические рекомендации от GigaChat на основе средних значений нескольких вегетационных индексов.
        """
        if not self.giga:
            return "Сервис AI-рекомендаций недоступен из-за отсутствия API ключа."

        # Формируем строку с данными для промпта
        stats_string = "\n".join([f"- {name.upper()}: {value:.3f}" for name, value in index_stats.items()])

        prompt = f"""
        Ты — ведущий агроном-аналитик, специализирующийся на данных дистанционного зондирования. Тебе предоставлены средние значения нескольких вегетационных индексов для сельскохозяйственного поля.

        СПРАВКА ПО ИНДЕКСАМ:
        - NDVI (Normalized Difference Vegetation Index): Основной показатель здоровья и густоты растительности. Высокие значения (ближе к 1) - хорошо.
        - SAVI (Soil-Adjusted Vegetation Index): Модификация NDVI, которая минимизирует влияние яркости почвы. Особенно полезен на ранних стадиях роста, когда почва видна.
        - EVI (Enhanced Vegetation Index): Улучшенный индекс, более чувствительный в областях с очень густой растительностью (где NDVI "насыщается") и менее подвержен атмосферным помехам.
        - VARI (Visible Atmospherically Resistant Index): Индекс, использующий только видимые каналы (RGB). Менее точен, чем индексы с NIR-каналом, но хорошо показывает неоднородность поля и устойчив к атмосферным искажениям.

        ДАННЫЕ АНАЛИЗА:
        {stats_string}

        ТВОЯ ЗАДАЧА:
        1. Проведи комплексный анализ, сравнивая значения индексов между собой. Например, что может означать высокий NDVI, но относительно низкий SAVI? Или как EVI дополняет картину NDVI?
        2. Дай общую оценку состояния посевов на основе всех данных.
        3. Сформируй 3-4 конкретные, действенные рекомендации для агронома в виде маркированного списка. Рекомендации должны учитывать нюансы, которые видны из сравнения индексов.
        4. Ответ должен быть структурированным, лаконичным и профессиональным. Не используй приветствия.
        """
        
        payload = Chat(
            messages=[
                Messages(
                    role=MessagesRole.USER,
                    content=prompt
                )
            ],
            temperature=0.7,
        )

        try:
            logger.info(f"Отправка запроса в GigaChat с данными: {index_stats}")
            async with self.giga as g: # Используем асинхронный контекстный менеджер
                response = await g.achat(payload)
            recommendation = response.choices[0].message.content
            logger.info("Ответ от GigaChat успешно получен.")
            return recommendation
        except Exception as e:
            logger.error(f"Ошибка при взаимодействии с API GigaChat: {e}")
            return f"Не удалось получить AI-рекомендации. Ошибка: {e}"
    # <<< --- КОНЕЦ ИЗМЕНЕНИЙ --- >>>

# --- END OF NEW FILE gigachat_service.py ---
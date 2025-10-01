import cv2
import matplotlib.pyplot as plt
import numpy as np
import requests
import ee  # Библиотека Google Earth Engine
import os  # Для работы с путями файлов и переменными окружения


class CropHealthAnalyzer:
    """
    Класс для анализа состояния посевов по спутниковым или дрон-снимкам.
    Позволяет вычислять и визуализировать вегетационные индексы VARI и NDVI
    как из локальных файлов, так и напрямую из Google Earth Engine.
    """
    EPSILON = 1e-8  # Константа для избежания деления на ноль

    def __init__(self, rgb_image_path=None, nir_image_path=None):
        """
        Инициализирует анализатор. Может быть создан пустым для последующей загрузки данных из GEE.
        """
        self.rgb_path = rgb_image_path
        self.nir_path = nir_image_path
        self.rgb_image = None
        self.nir_image = None
        self.vari_map = None
        self.ndvi_map = None

        if rgb_image_path:
            self._load_local_images()

    def _load_local_images(self):
        """(Приватный) Загружает изображения из локальных файлов."""
        img_bgr = cv2.imread(self.rgb_path)
        if img_bgr is None:
            raise FileNotFoundError(f"Ошибка: Не удалось загрузить RGB изображение: {self.rgb_path}")
        self.rgb_image = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        if self.nir_path:
            self.nir_image = cv2.imread(self.nir_path, cv2.IMREAD_GRAYSCALE)
            if self.nir_image is None:
                raise FileNotFoundError(f"Ошибка: Не удалось загрузить NIR изображение: {self.nir_path}")
            self._align_images()

    def _align_images(self):
        """(Приватный) Приводит размер NIR к размеру RGB, если они не совпадают."""
        if self.rgb_image is not None and self.nir_image is not None:
            if self.rgb_image.shape[:2] != self.nir_image.shape:
                print("Внимание: Размеры RGB и NIR не совпадают. Приводим NIR к размеру RGB.")
                h, w = self.rgb_image.shape[:2]
                self.nir_image = cv2.resize(self.nir_image, (w, h), interpolation=cv2.INTER_AREA)

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
                print("Локальный ключ не найден. Инициализация GEE с использованием стандартных учетных данных...")
                ee.Initialize()
        except Exception as e:
            raise ConnectionError(
                f"Ошибка инициализации Earth Engine. Убедитесь, что вы прошли аутентификацию ('earthengine authenticate') или положили файл 'gee_credentials.json' в папку со скриптом. Ошибка: {e}")

        point = ee.Geometry.Point([lon, lat])
        area_of_interest = point.buffer(buffer_size * 1000).bounds()

        collection = (ee.ImageCollection('COPERNICUS/S2_SR')
                      .filterBounds(area_of_interest)
                      .filterDate(start_date, end_date)
                      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)))

        if collection.size().getInfo() == 0:
            raise FileNotFoundError("Не найдено чистых снимков для указанного периода и местоположения.")

        image = collection.mosaic().clip(area_of_interest)
        rgb_params = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000}
        nir_params = {'bands': ['B8'], 'min': 0, 'max': 5000}

        rgb_url = image.getThumbURL(rgb_params)
        nir_url = image.getThumbURL(nir_params)

        analyzer = cls()
        print("Загрузка данных из Google Earth Engine...")
        analyzer.rgb_image = analyzer._url_to_numpy(rgb_url)
        analyzer.nir_image = analyzer._url_to_numpy(nir_url)[:, :, 0]
        print("Данные успешно загружены.")

        analyzer._align_images()
        return analyzer

    def calculate_vari(self) -> np.ndarray:
        """Вычисляет индекс VARI по RGB-изображению."""
        if self.rgb_image is None: raise ValueError("RGB изображение не загружено.")

        img_normalized = self.rgb_image.astype(float) / 255.0
        red, green, blue = img_normalized[:, :, 0], img_normalized[:, :, 1], img_normalized[:, :, 2]
        self.vari_map = (green - red) / (green + red - blue + self.EPSILON)
        return self.vari_map

    def calculate_ndvi(self) -> np.ndarray:
        """Вычисляет индекс NDVI, используя RGB и NIR изображения."""
        if self.rgb_image is None or self.nir_image is None:
            raise ValueError("Для расчета NDVI необходимы оба изображения: RGB и NIR.")

        red_channel = (self.rgb_image[:, :, 0]).astype(float) / 255.0
        nir_channel = self.nir_image.astype(float) / 255.0
        self.ndvi_map = (nir_channel - red_channel) / (nir_channel + red_channel + self.EPSILON)
        return self.ndvi_map

    def plot_results(self, index_name: str, cmap: str = 'RdYlGn'):
        """
        Отображает исходное изображение и рассчитанную карту вегетационного индекса.
        """
        index_map = self.vari_map if index_name.upper() == 'VARI' else self.ndvi_map
        if index_map is None:
            raise RuntimeError(f"Карта {index_name.upper()} не рассчитана.")

        fig, axes = plt.subplots(1, 2, figsize=(16, 7))
        axes[0].imshow(self.rgb_image)
        axes[0].set_title("Оригинальное изображение (RGB)")
        axes[0].axis('off')

        plot = axes[1].imshow(index_map, cmap=cmap, vmin=-1, vmax=1)
        axes[1].set_title(f"Карта индекса {index_name.upper()}")
        axes[1].axis('off')

        fig.colorbar(plot, ax=axes[1], orientation='vertical', label="Значение индекса")
        plt.suptitle(f"Анализ здоровья посевов (метод: {index_name.upper()})", fontsize=16)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()


# --- Главный блок исполнения ---
if __name__ == "__main__":
    print("--- Анализатор здоровья посевов ---")
    print("Выберите режим анализа:")
    print("1. Локальное RGB изображение (расчет индекса VARI)")
    print("2. Локальные RGB + NIR изображения (расчет индекса NDVI)")
    print("3. Получить снимок из Google Earth Engine (расчет NDVI или VARI)")

    choice = input("Введите номер режима (1, 2 или 3): ")

    try:
        if choice == '1':
            rgb_path = input("Введите путь к вашему RGB изображению: ")
            analyzer = CropHealthAnalyzer(rgb_image_path=rgb_path)
            analyzer.calculate_vari()
            analyzer.plot_results("VARI")

        elif choice == '2':
            rgb_path = input("Введите путь к вашему RGB изображению: ")
            nir_path = input("Введите путь к вашему NIR изображению: ")
            analyzer = CropHealthAnalyzer(rgb_image_path=rgb_path, nir_image_path=nir_path)
            analyzer.calculate_ndvi()
            analyzer.plot_results("NDVI")

        elif choice == '3':
            # --- Автоматический поиск ключа аутентификации ---
            # Скрипт ищет файл 'gee_credentials.json' в своей директории
            key_filename = 'gee_credentials.json'
            script_dir = os.path.dirname(os.path.abspath(__file__))
            local_key_path = os.path.join(script_dir, key_filename)

            # Если файл не существует, переменная останется None, и GEE использует стандартную аутентификацию
            if not os.path.exists(local_key_path):
                local_key_path = None

            print("\nВведите данные для поиска в Google Earth Engine.")
            lat = float(input("Широта (например, 55.75): "))
            lon = float(input("Долгота (например, 37.62): "))
            start_date = input("Дата начала в формате YYYY-MM-DD (например, 2023-07-01): ")
            end_date = input("Дата окончания в формате YYYY-MM-DD (например, 2023-07-31): ")

            analyzer = CropHealthAnalyzer.from_gee(
                lon, lat, start_date, end_date,
                service_account_key_path=local_key_path
            )

            index_choice = input("Какой индекс рассчитать? (1 - NDVI, 2 - VARI): ")
            if index_choice == '1':
                analyzer.calculate_ndvi()
                analyzer.plot_results("NDVI")
            elif index_choice == '2':
                analyzer.calculate_vari()
                analyzer.plot_results("VARI")
            else:
                print("Неверный выбор индекса.")
        else:
            print("Неверный выбор режима. Пожалуйста, запустите скрипт заново.")

    except Exception as e:
        print(f"\n[КРИТИЧЕСКАЯ ОШИБКА] Произошла ошибка во время выполнения: {e}")
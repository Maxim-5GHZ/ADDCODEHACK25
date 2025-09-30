import cv2
import matplotlib.pyplot as plt

class CropHealthAnalyzer:
    """
    Класс для анализа состояния посевов по спутниковым или дрон-снимкам.
    Позволяет вычислять и визуализировать вегетационные индексы VARI и NDVI.
    """
    EPSILON = 1e-8  # Небольшая константа для избежания деления на ноль

    def __init__(self, rgb_image_path, nir_image_path=None):
        """
        Инициализирует анализатор путями к изображениям.

        :param rgb_image_path: Строка, полный путь к RGB изображению.
        :param nir_image_path: Строка (опционально), полный путь к NIR изображению.
        """
        self.rgb_path = rgb_image_path
        self.nir_path = nir_image_path

        # Инициализируем атрибуты для хранения данных
        self.rgb_image = None
        self.nir_image = None
        self.vari_map = None
        self.ndvi_map = None

        # Сразу загружаем и подготавливаем изображения при создании объекта
        self._load_and_prepare_images()

    def _load_and_prepare_images(self):
        """
        Приватный метод для загрузки, конвертации и выравнивания изображений.
        """
        # --- Загрузка RGB ---
        img_bgr = cv2.imread(self.rgb_path)
        if img_bgr is None:
            raise FileNotFoundError(f"Ошибка: Не удалось загрузить RGB изображение: {self.rgb_path}")
        # Конвертируем в RGB для правильной работы и отображения
        self.rgb_image = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        # --- Загрузка NIR (если путь указан) ---
        if self.nir_path:
            img_nir = cv2.imread(self.nir_path, cv2.IMREAD_GRAYSCALE)
            if img_nir is None:
                raise FileNotFoundError(f"Ошибка: Не удалось загрузить NIR изображение: {self.nir_path}")
            self.nir_image = img_nir
            # Проверяем и выравниваем размеры, если необходимо
            self._align_images()

    def _align_images(self):
        """Приводит размер NIR изображения к размеру RGB, если они не совпадают."""
        if self.rgb_image.shape[:2] != self.nir_image.shape:
            print("Внимание: Размеры RGB и NIR изображений не совпадают. Приводим NIR к размеру RGB.")
            h, w = self.rgb_image.shape[:2]
            self.nir_image = cv2.resize(self.nir_image, (w, h), interpolation=cv2.INTER_AREA)

    def calculate_vari(self):
        """
        Вычисляет индекс VARI по RGB-изображению. Результат сохраняется в self.vari_map.
        """
        if self.rgb_image is None:
            print("Ошибка: RGB изображение не загружено.")
            return None

        # Нормализуем значения пикселей до диапазона [0, 1]
        img_normalized = self.rgb_image.astype(float) / 255.0
        red = img_normalized[:, :, 0]
        green = img_normalized[:, :, 1]
        blue = img_normalized[:, :, 2]

        # Рассчитываем VARI
        self.vari_map = (green - red) / (green + red - blue + self.EPSILON)
        return self.vari_map

    def calculate_ndvi(self):
        """
        Вычисляет индекс NDVI, используя RGB и NIR изображения. Результат сохраняется в self.ndvi_map.
        """
        if self.rgb_image is None or self.nir_image is None:
            raise ValueError("Ошибка: Для расчета NDVI необходимы оба изображения: RGB и NIR.")

        # Нормализуем каналы до диапазона [0, 1]
        # Для RGB изображения используем красный канал (индекс 0)
        red_channel = (self.rgb_image[:, :, 0]).astype(float) / 255.0
        nir_channel = self.nir_image.astype(float) / 255.0

        # Рассчитываем NDVI
        self.ndvi_map = (nir_channel - red_channel) / (nir_channel + red_channel + self.EPSILON)
        return self.ndvi_map

    def plot_results(self, index_name, cmap='RdYlGn'):
        """
        Отображает исходное изображение и рассчитанную карту вегетационного индекса.

        :param index_name: Строка, 'VARI' или 'NDVI'.
        :param cmap: Строка, цветовая карта для отображения индекса.
        """
        index_map = None
        if index_name.upper() == 'VARI':
            index_map = self.vari_map
            if index_map is None:
                raise RuntimeError("Ошибка: Карта VARI не рассчитана. Сначала вызовите метод calculate_vari().")
        elif index_name.upper() == 'NDVI':
            index_map = self.ndvi_map
            if index_map is None:
                raise RuntimeError("Ошибка: Карта NDVI не рассчитана. Сначала вызовите метод calculate_ndvi().")
        else:
            raise ValueError(f"Неизвестное имя индекса: {index_name}. Используйте 'VARI' или 'NDVI'.")

        fig, axes = plt.subplots(1, 2, figsize=(16, 7))

        axes[0].imshow(self.rgb_image)
        axes[0].set_title("Оригинальное изображение")
        axes[0].axis('off')

        plot = axes[1].imshow(index_map, cmap=cmap, vmin=-1, vmax=1)
        axes[1].set_title(f"Карта индекса {index_name.upper()}")
        axes[1].axis('off')

        fig.colorbar(plot, ax=axes[1], orientation='vertical', label=f"Значение индекса {index_name.upper()}")

        plt.suptitle(f"Анализ здоровья посевов (метод: {index_name.upper()})", fontsize=16)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()


# --- Главный блок исполнения (теперь он намного чище) ---
if __name__ == "__main__":
    print("--- Анализатор здоровья посевов ---")
    print("Выберите режим анализа:")
    print("1. Только RGB изображение (расчет индекса VARI)")
    print("2. RGB + Инфракрасное (NIR) изображение (расчет индекса NDVI)")

    choice = input("Введите номер режима (1 или 2): ")

    try:
        if choice == '1':
            rgb_path = input("Введите полный путь к вашему RGB изображению: ")
            analyzer = CropHealthAnalyzer(rgb_image_path=rgb_path)
            analyzer.calculate_vari()
            analyzer.plot_results("VARI")

        elif choice == '2':
            rgb_path = input("Введите полный путь к вашему RGB изображению: ")
            nir_path = input("Введите полный путь к вашему NIR изображению: ")
            analyzer = CropHealthAnalyzer(rgb_image_path=rgb_path, nir_image_path=nir_path)
            analyzer.calculate_ndvi()
            analyzer.plot_results("NDVI")

        else:
            print("Неверный выбор. Пожалуйста, запустите скрипт заново и введите 1 или 2.")

    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"\nПроизошла ошибка: {e}")
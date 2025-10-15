import numpy as np


class VegetationIndexCalculator:
    """
    Принимает готовые каналы (RGB для визуализации, Red, Green, Blue, NIR для
    расчетов) и выполняет вычисление и визуализацию индексов.
    """
    EPSILON = 1e-8
    L_SAVI = 0.5 # Коэффициент коррекции почвы для SAVI, стандартное значение
    # --- НОВЫЕ КОНСТАНТЫ ДЛЯ EVI ---
    G_EVI = 2.5
    C1_EVI = 6.0
    C2_EVI = 7.5
    L_EVI = 1.0

    def __init__(self, rgb_image: np.ndarray, red_channel: np.ndarray,
                 green_channel: np.ndarray, blue_channel: np.ndarray,
                 nir_channel: np.ndarray = None):
        """Инициализируется готовыми NumPy массивами."""
        if rgb_image is None:
            raise ValueError("RGB изображение (rgb_image) для визуализации должно быть предоставлено.")
        self.rgb_image = rgb_image
        self.red_channel = red_channel.astype(np.float32)
        self.green_channel = green_channel.astype(np.float32)
        self.blue_channel = blue_channel.astype(np.float32)
        self.nir_channel = nir_channel.astype(np.float32) if nir_channel is not None else None

        self.vari_map = None
        self.ndvi_map = None
        self.savi_map = None # Добавлено
        self.evi_map = None # Добавлено

    def calculate_vari(self) -> np.ndarray:
        """Вычисляет индекс VARI по научным данным каналов."""
        self.vari_map = ((self.green_channel - self.red_channel) /
                         (self.green_channel + self.red_channel - self.blue_channel + self.EPSILON))
        return self.vari_map

    def calculate_ndvi(self) -> np.ndarray:
        """Вычисляет индекс NDVI, используя научные данные Red и NIR каналов."""
        if self.nir_channel is None:
            raise ValueError("Для расчета NDVI необходим NIR канал (nir_channel).")

        self.ndvi_map = ((self.nir_channel - self.red_channel) /
                         (self.nir_channel + self.red_channel + self.EPSILON))
        return self.ndvi_map

    # --- НОВЫЙ МЕТОД ---
    def calculate_savi(self) -> np.ndarray:
        """Вычисляет индекс SAVI, который корректирует влияние почвы."""
        if self.nir_channel is None:
            raise ValueError("Для расчета SAVI необходим NIR канал (nir_channel).")

        numerator = self.nir_channel - self.red_channel
        denominator = self.nir_channel + self.red_channel + self.L_SAVI
        self.savi_map = ((numerator / (denominator + self.EPSILON)) * (1 + self.L_SAVI))
        return self.savi_map
        
    # --- НОВЫЙ МЕТОД ---
    def calculate_evi(self) -> np.ndarray:
        """Вычисляет улучшенный вегетационный индекс EVI."""
        if self.nir_channel is None:
            raise ValueError("Для расчета EVI необходим NIR канал (nir_channel).")
        
        # EVI = G * (NIR - Red) / (NIR + C1 * Red - C2 * Blue + L)
        numerator = self.nir_channel - self.red_channel
        denominator = (self.nir_channel + self.C1_EVI * self.red_channel - 
                       self.C2_EVI * self.blue_channel + self.L_EVI)
        
        self.evi_map = self.G_EVI * (numerator / (denominator + self.EPSILON))
        return self.evi_map
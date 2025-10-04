
import numpy as np


class VegetationIndexCalculator:
    """
    Принимает готовые каналы (RGB для визуализации, Red, Green, Blue, NIR для
    расчетов) и выполняет вычисление и визуализацию индексов.
    """
    EPSILON = 1e-8

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

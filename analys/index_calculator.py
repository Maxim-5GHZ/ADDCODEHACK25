# index_calculator.py

import numpy as np
import matplotlib.pyplot as plt


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

    def plot_results(self, index_name: str, cmap: str = 'RdYlGn'):
        """Отображает исходное изображение и рассчитанную карту индекса."""
        index_name = index_name.upper()
        index_map = self.vari_map if index_name == 'VARI' else self.ndvi_map

        if index_map is None:
            raise RuntimeError(f"Карта {index_name} не рассчитана. Вызовите сначала calculate_{index_name.lower()}().")

        fig, axes = plt.subplots(1, 2, figsize=(16, 7))
        axes[0].imshow(self.rgb_image)
        axes[0].set_title("Оригинальное изображение (RGB Визуализация)")
        axes[0].axis('off')

        plot = axes[1].imshow(index_map, cmap=cmap, vmin=-1, vmax=1)
        axes[1].set_title(f"Карта индекса {index_name}")
        axes[1].axis('off')

        fig.colorbar(plot, ax=axes[1], orientation='vertical', label="Значение индекса")
        plt.suptitle(f"Анализ здоровья посевов (метод: {index_name})", fontsize=16)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()
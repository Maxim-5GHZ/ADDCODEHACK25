import numpy as np
import matplotlib.pyplot as plt


class VegetationIndexCalculator:
    """
    Принимает готовые RGB, Red и NIR каналы и выполняет расчет вегетационных
    индексов (NDVI, VARI), а также их визуализацию.
    """
    EPSILON = 1e-8

    def __init__(self, rgb_image: np.ndarray, red_channel: np.ndarray = None, nir_channel: np.ndarray = None):
        """
        Инициализируется готовыми NumPy массивами изображений.
        """
        if rgb_image is None:
            raise ValueError("RGB изображение (rgb_image) должно быть предоставлено.")
        self.rgb_image = rgb_image
        self.red_channel = red_channel
        self.nir_channel = nir_channel
        self.vari_map = None
        self.ndvi_map = None

        # Если красный канал не передан отдельно, берем его из RGB
        if self.red_channel is None:
            self.red_channel = self.rgb_image[:, :, 0]

    def calculate_vari(self) -> np.ndarray:
        """Вычисляет индекс VARI по RGB-изображению."""
        img_normalized = self.rgb_image.astype(float) / 255.0
        red, green, blue = img_normalized[:, :, 0], img_normalized[:, :, 1], img_normalized[:, :, 2]
        self.vari_map = (green - red) / (green + red - blue + self.EPSILON)
        return self.vari_map

    def calculate_ndvi(self) -> np.ndarray:
        """Вычисляет индекс NDVI, используя предоставленные Red и NIR каналы."""
        if self.nir_channel is None:
            raise ValueError("Для расчета NDVI необходим NIR канал (nir_channel).")

        red = self.red_channel.astype(float) / 255.0
        nir = self.nir_channel.astype(float) / 255.0

        self.ndvi_map = (nir - red) / (nir + red + self.EPSILON)
        return self.ndvi_map

    def plot_results(self, index_name: str, cmap: str = 'RdYlGn'):
        """Отображает исходное изображение и рассчитанную карту индекса."""
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
# index_calculator.py

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches


class VegetationIndexCalculator:
    """
    Принимает готовые каналы, выполняет вычисление индексов,
    их статистический анализ, классификацию и визуализацию.
    """
    EPSILON = 1e-8

    def __init__(self, rgb_image: np.ndarray, red_channel: np.ndarray,
                 green_channel: np.ndarray, blue_channel: np.ndarray,
                 nir_channel: np.ndarray = None):
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
        """Вычисляет индекс VARI."""
        self.vari_map = np.clip(((self.green_channel - self.red_channel) /
                                 (self.green_channel + self.red_channel - self.blue_channel + self.EPSILON)), -1, 1)
        return self.vari_map

    def calculate_ndvi(self) -> np.ndarray:
        """Вычисляет индекс NDVI."""
        if self.nir_channel is None:
            raise ValueError("Для расчета NDVI необходим NIR канал.")
        self.ndvi_map = np.clip(((self.nir_channel - self.red_channel) /
                                 (self.nir_channel + self.red_channel + self.EPSILON)), -1, 1)
        return self.ndvi_map

    def calculate_index_stats(self, index_name: str) -> tuple[float, float]:
        """Вычисляет среднее и стандартное отклонение для рассчитанной карты индекса."""
        index_name = index_name.upper()
        if index_name == 'NDVI':
            index_map = self.ndvi_map
        elif index_name == 'VARI':
            index_map = self.vari_map
        else:
            raise ValueError("Неизвестное имя индекса. Используйте 'NDVI' или 'VARI'.")

        if index_map is None:
            raise RuntimeError(f"Карта {index_name} не рассчитана. Вызовите calculate_{index_name.lower()}().")

        mean_value = np.mean(index_map)
        std_dev_value = np.std(index_map)
        return mean_value, std_dev_value

    def plot_results(self, index_name: str, cmap: str = 'RdYlGn'):
        """Отображает исходное изображение, карту индекса и статистику."""
        index_name = index_name.upper()
        index_map = self.ndvi_map if index_name == 'NDVI' else self.vari_map

        if index_map is None:
            raise RuntimeError(f"Карта {index_name} не рассчитана.")

        fig, axes = plt.subplots(1, 2, figsize=(16, 7))
        axes[0].imshow(self.rgb_image)
        axes[0].set_title("Оригинальное изображение (RGB)")
        axes[0].axis('off')

        plot = axes[1].imshow(index_map, cmap=cmap, vmin=-1, vmax=1)
        axes[1].set_title(f"Карта индекса {index_name}")
        axes[1].axis('off')

        mean_val, std_val = self.calculate_index_stats(index_name)
        stats_text = f"Среднее (μ): {mean_val:.3f}\nСтд. откл. (σ): {std_val:.3f}"
        axes[1].text(0.02, 0.02, stats_text, transform=axes[1].transAxes,
                     fontsize=12, verticalalignment='bottom',
                     bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.7))

        fig.colorbar(plot, ax=axes[1], orientation='vertical', label="Значение индекса")
        plt.suptitle(f"Анализ вегетации (метод: {index_name})", fontsize=16)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()

    def classify_ndvi_by_threshold(self) -> tuple[np.ndarray, dict]:
        """
        Классифицирует карту NDVI по заданным порогам и вычисляет долю каждой зоны.
        """
        if self.ndvi_map is None:
            raise RuntimeError("Карта NDVI не рассчитана. Сначала вызовите calculate_ndvi().")

        class_map = np.zeros_like(self.ndvi_map, dtype=np.uint8)
        class_map[self.ndvi_map <= 0.2] = 1
        class_map[(self.ndvi_map > 0.2) & (self.ndvi_map <= 0.5)] = 2
        class_map[(self.ndvi_map > 0.5) & (self.ndvi_map <= 0.8)] = 3
        class_map[self.ndvi_map > 0.8] = 4

        total_pixels = class_map.size
        percentages = {
            "Почва/Низкая растительность (<= 0.2)": (np.sum(class_map == 1) / total_pixels) * 100,
            "Средняя плотность (0.2 - 0.5)": (np.sum(class_map == 2) / total_pixels) * 100,
            "Высокая плотность (0.5 - 0.8)": (np.sum(class_map == 3) / total_pixels) * 100,
            "Очень высокая плотность (> 0.8)": (np.sum(class_map == 4) / total_pixels) * 100,
        }

        return class_map, percentages

    def plot_classification_result(self, class_map: np.ndarray, percentages: dict):
        """Отображает карту классификации NDVI с легендой."""
        colors = ['#d73027', '#fee08b', '#a6d96a', '#1a9850']
        cmap = ListedColormap(colors)

        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        plot = ax.imshow(class_map, cmap=cmap)

        labels = percentages.keys()
        patches = [mpatches.Patch(color=colors[i], label=f"{list(labels)[i]}: {list(percentages.values())[i]:.2f}%") for
                   i in range(len(colors))]
        ax.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

        ax.set_title("Карта классификации зон вегетации по NDVI")
        ax.axis('off')
        plt.tight_layout(rect=[0, 0, 0.85, 1])
        plt.show()
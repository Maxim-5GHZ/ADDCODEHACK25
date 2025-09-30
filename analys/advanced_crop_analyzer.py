import cv2
import matplotlib.pyplot as plt


def calculate_vari_from_rgb(rgb_image_path):
    """
    Вычисляет индекс VARI по стандартному RGB-изображению.
    """
    # Читаем изображение (OpenCV загружает в формате BGR)
    img_bgr = cv2.imread(rgb_image_path)
    if img_bgr is None:
        print(f"Ошибка: Не удалось загрузить RGB изображение: {rgb_image_path}")
        return None, None

    # Конвертируем в RGB для правильного разделения каналов
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    # Нормализуем значения пикселей до диапазона [0, 1]
    img_normalized = img_rgb.astype(float) / 255.0

    red = img_normalized[:, :, 0]
    green = img_normalized[:, :, 1]
    blue = img_normalized[:, :, 2]

    # Рассчитываем VARI, избегая деления на ноль
    epsilon = 1e-8
    vari = (green - red) / (green + red - blue + epsilon)

    return vari, img_rgb


def calculate_ndvi_from_files(rgb_image_path, nir_image_path):
    """
    Вычисляет индекс NDVI, используя RGB-изображение (для красного канала)
    и отдельное изображение в ближнем инфракрасном спектре (NIR).
    """
    # Читаем RGB изображение
    img_bgr = cv2.imread(rgb_image_path)
    if img_bgr is None:
        print(f"Ошибка: Не удалось загрузить RGB изображение: {rgb_image_path}")
        return None, None

    # Читаем NIR изображение как одноканальное (в градациях серого)
    img_nir = cv2.imread(nir_image_path, cv2.IMREAD_GRAYSCALE)
    if img_nir is None:
        print(f"Ошибка: Не удалось загрузить NIR изображение: {nir_image_path}")
        return None, None

    # Проверяем, совпадают ли размеры изображений
    if img_bgr.shape[:2] != img_nir.shape:
        print("Внимание: Размеры RGB и NIR изображений не совпадают. Приводим NIR к размеру RGB.")
        # Изменяем размер NIR изображения до размеров RGB
        img_nir = cv2.resize(img_nir, (img_bgr.shape[1], img_bgr.shape[0]), interpolation=cv2.INTER_AREA)

    # Нормализуем оба изображения до диапазона [0, 1]
    red_channel = (img_bgr[:, :, 2]).astype(float) / 255.0  # Красный канал в BGR это индекс 2
    nir_channel = img_nir.astype(float) / 255.0

    # Рассчитываем NDVI, избегая деления на ноль
    epsilon = 1e-8
    ndvi = (nir_channel - red_channel) / (nir_channel + red_channel + epsilon)

    # Возвращаем RGB версию изображения для визуализации
    img_rgb_display = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    return ndvi, img_rgb_display


def plot_results(original_image, index_map, index_name, cmap='RdYlGn'):
    """
    Отображает исходное изображение и рассчитанную карту вегетационного индекса.
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    axes[0].imshow(original_image)
    axes[0].set_title("Оригинальное изображение")
    axes[0].axis('off')

    # Отображаем карту индекса
    plot = axes[1].imshow(index_map, cmap=cmap, vmin=-1, vmax=1)
    axes[1].set_title(f"Карта индекса {index_name}")
    axes[1].axis('off')

    # Добавляем цветовую шкалу
    fig.colorbar(plot, ax=axes[1], orientation='vertical', label=f"Значение индекса {index_name}")

    plt.suptitle(f"Анализ здоровья посевов (метод: {index_name})", fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()


# --- Главный блок исполнения ---
if __name__ == "__main__":
    print("--- Анализатор здоровья посевов ---")
    print("Выберите режим анализа:")
    print("1. Только RGB изображение (расчет индекса VARI)")
    print("2. RGB + Инфракрасное (NIR) изображение (расчет индекса NDVI)")

    choice = input("Введите номер режима (1 или 2): ")

    if choice == '1':
        rgb_path = input("Введите полный путь к вашему RGB изображению: ")
        vari_map, original_img = calculate_vari_from_rgb(rgb_path)
        if vari_map is not None:
            plot_results(original_img, vari_map, "VARI")

    elif choice == '2':
        rgb_path = input("Введите полный путь к вашему RGB изображению: ")
        nir_path = input("Введите полный путь к вашему NIR изображению: ")
        ndvi_map, original_img = calculate_ndvi_from_files(rgb_path, nir_path)
        if ndvi_map is not None:
            plot_results(original_img, ndvi_map, "NDVI")

    else:
        print("Неверный выбор. Пожалуйста, запустите скрипт заново и введите 1 или 2.")
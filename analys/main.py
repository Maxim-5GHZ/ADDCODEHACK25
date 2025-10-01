import os
from image_provider import ImageProvider
from index_calculator import VegetationIndexCalculator


def main():
    """Главная функция, управляющая логикой приложения."""
    print("--- Анализатор здоровья посевов ---")
    print("Выберите режим анализа:")
    print("1. Локальное RGB изображение (расчет VARI)")
    print("2. Локальные RGB + NIR изображения (расчет NDVI)")
    print("3. Снимок из Google Earth Engine (расчет NDVI или VARI)")

    choice = input("Введите номер режима (1, 2 или 3): ")

    try:
        image_provider = None

        if choice == '1':
            rgb_path = input("Введите путь к вашему RGB изображению: ")
            image_provider = ImageProvider(rgb_image_path=rgb_path)

        elif choice == '2':
            rgb_path = input("Введите путь к вашему RGB изображению: ")
            nir_path = input("Введите путь к вашему NIR изображению: ")
            image_provider = ImageProvider(rgb_image_path=rgb_path, nir_image_path=nir_path)

        elif choice == '3':
            key_filename = 'auth_file.json'
            script_dir = os.path.dirname(os.path.abspath(__file__))
            local_key_path = os.path.join(script_dir, key_filename)
            if not os.path.exists(local_key_path):
                local_key_path = None

            print("\nВведите данные для поиска в Google Earth Engine.")
            lat = float(input("Широта (например, 55.75): "))
            lon = float(input("Долгота (например, 37.62): "))
            start_date = input("Дата начала (YYYY-MM-DD, например, 2023-07-01): ")
            end_date = input("Дата окончания (YYYY-MM-DD, например, 2023-07-31): ")

            image_provider = ImageProvider.from_gee(
                lon, lat, start_date, end_date, service_account_key_path=local_key_path
            )
        else:
            print("Неверный выбор режима. Пожалуйста, запустите скрипт заново.")
            return

        # Шаг 2: Расчет и визуализация, если изображения были получены
        if image_provider and image_provider.rgb_image is not None:
            calculator = VegetationIndexCalculator(
                rgb_image=image_provider.rgb_image,
                red_channel=image_provider.red_channel,
                nir_channel=image_provider.nir_channel
            )

            if choice == '1':
                calculator.calculate_vari()
                calculator.plot_results("VARI")
            elif choice == '2':
                calculator.calculate_ndvi()
                calculator.plot_results("NDVI")
            elif choice == '3':
                index_choice = input("Какой индекс рассчитать? (1 - NDVI, 2 - VARI): ")
                if index_choice == '1':
                    calculator.calculate_ndvi()
                    calculator.plot_results("NDVI")
                elif index_choice == '2':
                    calculator.calculate_vari()
                    calculator.plot_results("VARI")
                else:
                    print("Неверный выбор индекса.")

    except Exception as e:
        print(f"\n[КРИТИЧЕСКАЯ ОШИБКА] Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
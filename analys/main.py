# main.py

import os
from image_provider import ImageProvider
from index_calculator import VegetationIndexCalculator


def get_validated_float(prompt: str) -> float:
    """Запрашивает у пользователя ввод, пока не будет введено корректное число."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("[Ошибка] Пожалуйста, введите корректное число (например, 45.04).")


def get_validated_path(prompt: str) -> str:
    """Запрашивает у пользователя путь к файлу, пока не будет введен существующий путь."""
    while True:
        path = input(prompt).strip().replace("'", "").replace('"', '')
        if os.path.exists(path):
            return path
        else:
            print(f"[Ошибка] Файл не найден по пути: {path}. Пожалуйста, проверьте путь.")


def main():
    """Главная функция, управляющая логикой приложения."""
    print("--- Анализатор здоровья посевов ---")
    print("Выберите режим анализа:")
    print("1. Локальное RGB изображение (расчет индекса VARI)")
    print("2. Локальные RGB + NIR изображения (расчет индекса NDVI)")
    print("3. Снимок из Google Earth Engine (расчет NDVI или VARI)")

    choice = input("Введите номер режима (1, 2 или 3): ")

    try:
        image_provider = None

        if choice == '1':
            rgb_path = get_validated_path("Введите путь к вашему RGB изображению: ")
            image_provider = ImageProvider(rgb_image_path=rgb_path)
        elif choice == '2':
            rgb_path = get_validated_path("Введите путь к вашему RGB изображению: ")
            nir_path = get_validated_path("Введите путь к вашему NIR изображению: ")
            image_provider = ImageProvider(rgb_image_path=rgb_path, nir_image_path=nir_path)
        elif choice == '3':
            key_filename = 'auth_file.json'
            script_dir = os.path.dirname(os.path.abspath(__file__))
            local_key_path = os.path.join(script_dir, key_filename)
            if not os.path.exists(local_key_path):
                print(
                    f"\n[Внимание] Файл ключа '{key_filename}' не найден. Будет использована стандартная аутентификация.")
                local_key_path = None
            print("\nВведите данные для поиска в Google Earth Engine.")
            lat = get_validated_float("Широта (например, 45.04): ")
            lon = get_validated_float("Долгота (например, 39.17): ")
            start_date = input("Дата начала (YYYY-MM-DD, например, 2024-07-01): ")
            end_date = input("Дата окончания (YYYY-MM-DD, например, 2024-08-31): ")

            image_provider = ImageProvider.from_gee(
                lon, lat, start_date, end_date, buffer_size_km=0.5, service_account_key_path=local_key_path
            )
        else:
            print("Неверный выбор режима. Завершение программы.")
            return

        if image_provider and image_provider.rgb_image is not None:
            calculator = VegetationIndexCalculator(
                rgb_image=image_provider.rgb_image, red_channel=image_provider.red_channel,
                green_channel=image_provider.green_channel, blue_channel=image_provider.blue_channel,
                nir_channel=image_provider.nir_channel
            )

            # Логика расчета и визуализации
            index_to_run = ""
            if choice == '1':
                index_to_run = "VARI"
            elif choice == '2':
                index_to_run = "NDVI"
            elif choice == '3':
                index_choice = input("Какой индекс рассчитать? (1 - NDVI, 2 - VARI): ").strip()
                if index_choice == '1':
                    index_to_run = "NDVI"
                elif index_choice == '2':
                    index_to_run = "VARI"
                else:
                    print("Неверный выбор индекса.")

            if index_to_run:
                print(f"\nРасчет индекса {index_to_run}...")
                # Динамический вызов calculate_ndvi() или calculate_vari()
                getattr(calculator, f'calculate_{index_to_run.lower()}')()
                mean, std = calculator.calculate_index_stats(index_to_run)
                print(f"Среднее {index_to_run}: {mean:.4f}, Стандартное отклонение: {std:.4f}")
                calculator.plot_results(index_to_run)

                # Опциональный шаг классификации для NDVI
                if index_to_run == 'NDVI':
                    run_classification = input("\nВыполнить классификацию зон по NDVI? (y/n): ").lower().strip()
                    if run_classification == 'y':
                        print("Выполнение классификации...")
                        class_map, percentages = calculator.classify_ndvi_by_threshold()
                        print("\n--- Результаты классификации (доля площади) ---")
                        for name, perc in percentages.items():
                            print(f"- {name}: {perc:.2f}%")
                        calculator.plot_classification_result(class_map, percentages)

    except Exception as e:
        print(f"\n[КРИТИЧЕСКАЯ ОШИБКА] Программа завершилась с ошибкой: {e}")


if __name__ == "__main__":
    main()
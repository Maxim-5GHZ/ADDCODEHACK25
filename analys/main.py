# main.py

import os
from datetime import datetime
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


# --- НОВАЯ ФУНКЦИЯ ДЛЯ СОХРАНЕНИЯ ОТЧЕТА ---
def save_report_to_file(filepath: str, metadata: dict, stats: tuple, percentages: dict):
    """
    Формирует и сохраняет текстовый отчет по результатам анализа.

    Args:
        filepath (str): Путь для сохранения файла.
        metadata (dict): Информация об источнике данных (координаты, даты, пути).
        stats (tuple): Кортеж со средним значением и стандартным отклонением.
        percentages (dict): Словарь с процентами площадей для каждого класса.
    """
    mean_val, std_val = stats

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 40 + "\n")
            f.write("    ОТЧЕТ ПО АНАЛИЗУ ВЕГЕТАЦИИ (NDVI)\n")
            f.write("=" * 40 + "\n\n")

            f.write(f"Дата и время анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("--- Источник данных ---\n")
            for key, value in metadata.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")

            f.write("--- Общая статистика NDVI ---\n")
            f.write(f"Среднее значение (μ): {mean_val:.4f}\n")
            f.write(f"Стандартное отклонение (σ): {std_val:.4f}\n\n")

            f.write("--- Классификация зон (доля площади) ---\n")
            for name, perc in percentages.items():
                f.write(f"- {name}: {perc:.2f}%\n")

            f.write("\n\n" + "=" * 40 + "\n")
            f.write("        Отчет сгенерирован автоматически\n")
            f.write("=" * 40 + "\n")

        print(f"\n[Успешно] Отчет сохранен в файл: {filepath}")

    except Exception as e:
        print(f"\n[Ошибка] Не удалось сохранить отчет в файл. Причина: {e}")


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
        analysis_metadata = {}  # Словарь для хранения информации для отчета

        if choice == '1':
            rgb_path = get_validated_path("Введите путь к вашему RGB изображению: ")
            image_provider = ImageProvider(rgb_image_path=rgb_path)
            analysis_metadata = {"Тип": "Локальный файл (VARI)", "RGB файл": rgb_path}
        elif choice == '2':
            rgb_path = get_validated_path("Введите путь к вашему RGB изображению: ")
            nir_path = get_validated_path("Введите путь к вашему NIR изображению: ")
            image_provider = ImageProvider(rgb_image_path=rgb_path, nir_image_path=nir_path)
            analysis_metadata = {"Тип": "Локальные файлы (NDVI)", "RGB файл": rgb_path, "NIR файл": nir_path}
        elif choice == '3':
            key_filename = 'auth_file.json'
            script_dir = os.path.dirname(os.path.abspath(__file__))
            local_key_path = os.path.join(script_dir, key_filename)
            if not os.path.exists(local_key_path):
                print(f"\n[Внимание] Файл ключа '{key_filename}' не найден.")
                local_key_path = None
            print("\nВведите данные для поиска в Google Earth Engine.")
            lat = get_validated_float("Широта (например, 45.04): ")
            lon = get_validated_float("Долгота (например, 39.17): ")
            start_date = input("Дата начала (YYYY-MM-DD): ")
            end_date = input("Дата окончания (YYYY-MM-DD): ")
            image_provider = ImageProvider.from_gee(
                lon, lat, start_date, end_date, buffer_size_km=0.5, service_account_key_path=local_key_path
            )
            analysis_metadata = {
                "Тип": "Google Earth Engine", "Широта": lat, "Долгота": lon,
                "Начальная дата": start_date, "Конечная дата": end_date
            }
        else:
            print("Неверный выбор режима.")
            return

        if image_provider and image_provider.rgb_image is not None:
            calculator = VegetationIndexCalculator(
                rgb_image=image_provider.rgb_image, red_channel=image_provider.red_channel,
                green_channel=image_provider.green_channel, blue_channel=image_provider.blue_channel,
                nir_channel=image_provider.nir_channel
            )

            index_to_run = ""
            # ... (Логика выбора индекса остается прежней) ...
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

            if index_to_run:
                print(f"\nРасчет индекса {index_to_run}...")
                getattr(calculator, f'calculate_{index_to_run.lower()}')()
                mean, std = calculator.calculate_index_stats(index_to_run)
                print(f"Среднее {index_to_run}: {mean:.4f}, Стандартное отклонение: {std:.4f}")
                calculator.plot_results(index_to_run)

                if index_to_run == 'NDVI':
                    run_classification = input("\nВыполнить классификацию зон по NDVI? (y/n): ").lower().strip()
                    if run_classification == 'y':
                        print("Выполнение классификации...")
                        class_map, percentages = calculator.classify_ndvi_by_threshold()
                        print("\n--- Результаты классификации (доля площади) ---")
                        for name, perc in percentages.items():
                            print(f"- {name}: {perc:.2f}%")
                        calculator.plot_classification_result(class_map, percentages)

                        # --- НОВЫЙ БЛОК ДЛЯ СОХРАНЕНИЯ ОТЧЕТА ---
                        save_choice = input(
                            "\nСохранить отчет о классификации в текстовый файл? (y/n): ").lower().strip()
                        if save_choice == 'y':
                            default_filename = f"report_ndvi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                            output_path = input(f"Введите имя файла [по умолчанию: {default_filename}]: ").strip()
                            if not output_path:
                                output_path = default_filename

                            save_report_to_file(output_path, analysis_metadata, (mean, std), percentages)

    except Exception as e:
        print(f"\n[КРИТИЧЕСКАЯ ОШИБКА] Программа завершилась с ошибкой: {e}")


if __name__ == "__main__":
    main()
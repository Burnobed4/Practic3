"""Модуль для генерации финансовых отчетов.

Предоставляет функции для создания отчетов по категориям и периодам.
"""

import csv
from typing import Dict
from .database import get_category_report_from_db, get_period_report_from_db


def generate_category_report(period: str = "month", output_file: str = None) -> Dict:
    """Генерирует отчет по категориям за указанный период.

    Args:
        period (str, optional): Период для отчета.
            Допустимые значения: 'today', 'month', 'all'. По умолчанию 'month'.
        output_file (str, optional): Путь для сохранения отчета в CSV.
            По умолчанию None.

    Returns:
        Dict: Словарь с данными отчета.
    """
    # Используем функцию из database.py для эффективной работы с БД
    report = get_category_report_from_db(period)

    if output_file:
        save_report_to_csv(report, output_file)

    return report


def generate_period_report(start_date: str, end_date: str, output_file: str = None) -> Dict:
    """Генерирует отчет за указанный период времени.

    Args:
        start_date (str): Начальная дата в формате YYYY-MM-DD.
        end_date (str): Конечная дата в формате YYYY-MM-DD.
        output_file (str, optional): Путь для сохранения отчета в CSV.
            По умолчанию None.

    Returns:
        Dict: Словарь с данными отчета.
    """
    # Используем функцию из database.py для эффективной работы с БД
    report = get_period_report_from_db(start_date, end_date)

    if output_file:
        save_report_to_csv(report, output_file)

    return report


def save_report_to_csv(report: Dict, filename: str):
    """Сохраняет отчет в CSV файл.

    Args:
        report (Dict): Данные отчета.
        filename (str): Имя файла для сохранения.

    Raises:
        IOError: Если возникает ошибка при записи файла.
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            writer.writerow(["Финансовый отчет"])
            writer.writerow(["Период:", report["period"]])
            writer.writerow(["Всего операций:", report["total_expenses"]])
            writer.writerow(["Общая сумма:", f"{report['total_amount']:.2f}"])
            writer.writerow(["Сгенерировано:", report["generated_at"]])
            writer.writerow([])

            if "categories" in report:
                writer.writerow(["Категория", "Сумма"])
                for category, amount in report["categories"]:
                    writer.writerow([category, f"{amount:.2f}"])
            elif "daily_totals" in report:
                writer.writerow(["Дата", "Сумма"])
                for date, amount in report["daily_totals"].items():
                    writer.writerow([date, f"{amount:.2f}"])

        print(f"Отчет сохранен в файл: {filename}")
    except IOError as e:
        print(f"Ошибка сохранения отчета: {e}")


def print_report(report: Dict):
    """Выводит отчет в консоль в читаемом формате.

    Args:
        report (Dict): Данные отчета для вывода.
    """
    print(f"\n=== ФИНАНСОВЫЙ ОТЧЕТ ===")
    print(f"Период: {report['period']}")
    print(f"Операций: {report['total_expenses']}")
    print(f"Общая сумма: {report['total_amount']:.2f} руб.")
    print(f"Сгенерирован: {report['generated_at']}")

    if "categories" in report:
        print("\n--- По категориям ---")
        for category, amount in report["categories"]:
            print(f"  {category}: {amount:.2f} руб.")

    if "daily_totals" in report:
        print("\n--- По дням ---")
        for date, amount in report["daily_totals"].items():
            print(f"  {date}: {amount:.2f} руб.")
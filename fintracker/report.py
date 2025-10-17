import csv
from datetime import datetime
from typing import List, Dict
from .storage import get_expenses, get_categories


def generate_category_report(period: str = "month", output_file: str = None) -> Dict:
    expenses = get_expenses(period)

    # Группируем по категориям
    category_totals = {}
    for expense in expenses:
        if expense.category not in category_totals:
            category_totals[expense.category] = 0
        category_totals[expense.category] += expense.amount

    # Сортируем по сумме (по убыванию)
    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)

    report = {
        "period": period,
        "total_expenses": len(expenses),
        "total_amount": sum(exp.amount for exp in expenses),
        "categories": sorted_categories,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if output_file:
        save_report_to_csv(report, output_file)

    return report


def generate_period_report(start_date: str, end_date: str, output_file: str = None) -> Dict:
    all_expenses = get_expenses("all")

    # Фильтруем по дате
    filtered_expenses = []
    for expense in all_expenses:
        exp_date = expense.date.split()[0]  # Берем только дату без времени
        if start_date <= exp_date <= end_date:
            filtered_expenses.append(expense)

    # Группируем по дням
    daily_totals = {}
    for expense in filtered_expenses:
        date = expense.date.split()[0]
        if date not in daily_totals:
            daily_totals[date] = 0
        daily_totals[date] += expense.amount

    report = {
        "period": f"{start_date} - {end_date}",
        "total_expenses": len(filtered_expenses),
        "total_amount": sum(exp.amount for exp in filtered_expenses),
        "daily_totals": daily_totals,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if output_file:
        save_report_to_csv(report, output_file)

    return report


def save_report_to_csv(report: Dict, filename: str):
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
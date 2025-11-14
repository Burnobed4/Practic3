"""Тестовый скрипт для проверки документации."""

from fintracker import storage, models, commands, report


def test_help():
    """Тестирует отображение документации через help()."""
    print("=== Тестирование документации ===\n")

    print("1. Модуль storage:")
    help(storage)

    print("\n2. Класс Expense:")
    help(models.Expense)

    print("\n3. Функция add_expense:")
    help(storage.add_expense)

    print("\n4. Функция generate_category_report:")
    help(report.generate_category_report)

    print("\n5. Функция handle_category:")
    help(commands.handle_category)

if __name__ == "__main__":
    test_help()
import argparse
from .storage import add_expense, get_expenses, add_category, get_categories
from .report import generate_category_report, generate_period_report, print_report


def handle_add(args):
    """Обработка команды добавления операции"""
    try:
        success = add_expense(args.category, args.amount, args.description)
        if success:
            type_str = "расход" if args.amount < 0 else "доход"
            print(f"Добавлен {type_str}: {args.category} - {abs(args.amount):.2f} руб.")
        return success
    except ValueError as e:
        print(f"Ошибка: {e}")
        return False


def handle_list(args):
    """Обработка команды просмотра операций"""
    expenses = get_expenses(args.period)

    if not expenses:
        print("Нет операций за указанный период")
        return

    print(f"\nСписок операций ({args.period}):")
    print("-" * 50)
    total = 0
    for i, expense in enumerate(expenses, 1):
        sign = "-" if expense.amount < 0 else "+"
        print(
            f"{i}. {expense.date} | {expense.category:15} | {sign} {abs(expense.amount):8.2f} руб. | {expense.description}")
        total += expense.amount

    print("-" * 50)
    print(f"Итого: {total:+.2f} руб.")


def handle_report(args):
    """Обработка команды генерации отчета"""
    if args.type == "category":
        report = generate_category_report(args.period, args.output)
    elif args.type == "period" and args.start and args.end:
        report = generate_period_report(args.start, args.end, args.output)
    else:
        print("Для отчета за период укажите --start и --end")
        return

    if not args.output:
        print_report(report)


def handle_category(args):
    """Обработка команды работы с категориями"""
    if args.action == "add":
        success = add_category(args.name, args.type)
        if success:
            print(f"Добавлена категория: {args.name} ({args.type})")
    elif args.action == "list":
        categories = get_categories()
        if not categories:
            print("Нет категорий")
            return

        print("\nСписок категорий:")
        for category in categories:
            print(f"  {category.name} ({category.type})")


def setup_commands():
    parser = argparse.ArgumentParser(description="Финансовый трекер расходов")
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

    # Команда добавления
    add_parser = subparsers.add_parser("add", help="Добавить операцию")
    add_parser.add_argument("--category", "-c", required=True, help="Категория операции")
    add_parser.add_argument("--amount", "-a", type=float, required=True, help="Сумма (отрицательная для расходов)")
    add_parser.add_argument("--description", "-d", default="", help="Описание операции")

    # Команда просмотра
    list_parser = subparsers.add_parser("list", help="Просмотреть операции")
    list_parser.add_argument("--period", "-p", choices=["today", "month", "all"], default="all", help="Период")

    # Команда отчетов
    report_parser = subparsers.add_parser("report", help="Сгенерировать отчет")
    report_parser.add_argument("--type", "-t", choices=["category", "period"], required=True, help="Тип отчета")
    report_parser.add_argument("--period", "-p", choices=["today", "month", "all"], default="month",
                               help="Период (для category)")
    report_parser.add_argument("--start", help="Начальная дата (YYYY-MM-DD) для period")
    report_parser.add_argument("--end", help="Конечная дата (YYYY-MM-DD) для period")
    report_parser.add_argument("--output", "-o", help="Файл для сохранения отчета (CSV)")

    # Команда категорий
    cat_parser = subparsers.add_parser("category", help="Управление категориями")
    cat_parser.add_argument("action", choices=["add", "list"], help="Действие")
    cat_parser.add_argument("--name", "-n", help="Название категории (для add)")
    cat_parser.add_argument("--type", "-t", choices=["expense", "income"], help="Тип категории (для add)")

    return parser
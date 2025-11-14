import sys
from fintracker.commands import setup_commands, handle_add, handle_list, handle_report, handle_category


def main():
    """Основная функция приложения.

    Обрабатывает аргументы командной строки и вызывает соответствующие обработчики.
    """
    parser = setup_commands()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "add":
            handle_add(args)
        elif args.command == "list":
            handle_list(args)
        elif args.command == "report":
            handle_report(args)
        elif args.command == "category":
            handle_category(args)
        else:
            print("Неизвестная команда")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
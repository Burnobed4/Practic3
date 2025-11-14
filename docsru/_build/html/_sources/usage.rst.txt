Руководство пользователя
========================

Команда add
-----------

Добавляет новую финансовую операцию.

**Синтаксис:**:

    py main.py add --category CATEGORY --amount AMOUNT [--description TEXT]

**Параметры:**

- ``--category, -c``: Категория операции (обязательный)
- ``--amount, -a``: Сумма операции (обязательный, отрицательная для расходов)
- ``--description, -d``: Описание операции (опциональный)

**Примеры:**:

    # Добавление расхода
    py main.py add --category "еда" --amount -250 --description "Обед в кафе"

    # Добавление дохода
    py main.py add --category "зарплата" --amount 50000 --description "Зарплата за месяц"

    # Короткая версия
    py main.py add -c "транспорт" -a -50 -d "Метро"

Команда list
------------

Просмотр операций за указанный период.

**Синтаксис:**:

    py main.py list [--period today|month|all]

**Параметры:**

- ``--period, -p``: Период для фильтрации (по умолчанию: all)

**Примеры:**:

    py main.py list --period today
    py main.py list --period month
    py main.py list -p all

Команда report
--------------

Генерация финансовых отчетов.

**Синтаксис:**:

    # Отчет по категориям
    py main.py report --type category [--period today|month|all] [--output FILE.csv]

    # Отчет за период
    py main.py report --type period --start YYYY-MM-DD --end YYYY-MM-DD [--output FILE.csv]

**Примеры:**:

    # Отчет по категориям за месяц
    py main.py report --type category --period month

    # Отчет за период с сохранением в файл
    py main.py report --type period --start 2024-01-01 --end 2024-01-31 --output january_report.csv

Команда category
----------------

Управление категориями операций.

**Синтаксис:**:

    # Добавление категории
    py main.py category add --name NAME --type expense|income

    # Просмотр категорий
    py main.py category list

**Примеры:**:

    py main.py category add --name "транспорт" --type expense
    py main.py category add --name "зарплата" --type income
    py main.py category list
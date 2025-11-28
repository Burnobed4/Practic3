"""
Модульные тесты для приложения Финансовый Трекер.
"""

import unittest
import os
import tempfile
import shutil
from datetime import datetime
from fintracker.models import Expense, Category
from fintracker.storage import add_expense, get_expenses, add_category, get_categories, init_storage
from fintracker.report import generate_category_report, generate_period_report
from fintracker.database import get_connection, DATABASE_FILE


class TestModels(unittest.TestCase):
    """Тесты для моделей данных."""

    def test_category_creation(self):
        """Тест создания объекта Category и его методов."""
        category = Category("еда", "expense")

        self.assertEqual(category.name, "еда")
        self.assertEqual(category.type, "expense")

        # Тест метода to_dict
        category_dict = category.to_dict()
        self.assertEqual(category_dict["name"], "еда")
        self.assertEqual(category_dict["type"], "expense")

        # Тест метода from_dict
        new_category = Category.from_dict(category_dict)
        self.assertEqual(new_category.name, "еда")
        self.assertEqual(new_category.type, "expense")

    def test_expense_creation(self):
        """Тест создания объекта Expense и его методов."""
        expense = Expense("еда", -250.50, "Обед в кафе")

        self.assertEqual(expense.category, "еда")
        self.assertEqual(expense.amount, -250.50)
        self.assertEqual(expense.description, "Обед в кафе")
        self.assertIsNotNone(expense.date)

        # Тест метода to_dict
        expense_dict = expense.to_dict()
        self.assertEqual(expense_dict["category"], "еда")
        self.assertEqual(expense_dict["amount"], -250.50)
        self.assertEqual(expense_dict["description"], "Обед в кафе")

        # Тест метода from_dict
        new_expense = Expense.from_dict(expense_dict)
        self.assertEqual(new_expense.category, "еда")
        self.assertEqual(new_expense.amount, -250.50)
        self.assertEqual(new_expense.description, "Обед в кафе")

    def test_expense_with_custom_date(self):
        """Тест создания Expense с пользовательской датой."""
        custom_date = "2025-01-15 12:30:00"
        expense = Expense("транспорт", -50.0, "Такси", custom_date)

        self.assertEqual(expense.date, custom_date)


class TestStorage(unittest.TestCase):
    """Тесты для функциональности хранения данных."""

    def setUp(self):
        """Настройка временной БД для тестов."""
        self.test_dir = tempfile.mkdtemp()
        self.test_db_file = os.path.join(self.test_dir, "test_financial.db")

        # Патчим DATABASE_FILE для использования тестовой БД
        import fintracker.database
        self.original_db_file = fintracker.database.DATABASE_FILE
        fintracker.database.DATABASE_FILE = self.test_db_file

        # Инициализируем тестовую БД
        init_storage()

    def tearDown(self):
        """Очистка после тестов."""
        import fintracker.database
        fintracker.database.DATABASE_FILE = self.original_db_file

        # Закрываем все соединения и удаляем тестовую БД
        if os.path.exists(self.test_db_file):
            os.unlink(self.test_db_file)
        shutil.rmtree(self.test_dir)

    def test_add_expense(self):
        """Тест добавления новой траты."""
        # Сначала добавляем категорию
        add_category("еда", "expense")

        success = add_expense("еда", -250, "Тестовая трата")
        self.assertTrue(success)

        expenses = get_expenses("all")
        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0].category, "еда")
        self.assertEqual(expenses[0].amount, -250)
        self.assertEqual(expenses[0].description, "Тестовая трата")

    def test_add_income(self):
        """Тест добавления дохода (положительная сумма)."""
        # Сначала добавляем категорию
        add_category("зарплата", "income")

        success = add_expense("зарплата", 50000, "Зарплата за месяц")
        self.assertTrue(success)

        expenses = get_expenses("all")
        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0].amount, 50000)
        self.assertEqual(expenses[0].category, "зарплата")

    def test_get_expenses_all(self):
        """Тест получения всех трат."""
        # Добавляем категории и тестовые траты
        add_category("еда", "expense")
        add_category("транспорт", "expense")

        add_expense("еда", -100, "Тест 1")
        add_expense("транспорт", -50, "Тест 2")

        expenses = get_expenses("all")
        self.assertEqual(len(expenses), 2)

    def test_get_expenses_today(self):
        """Тест получения сегодняшних трат."""
        add_category("еда", "expense")
        add_expense("еда", -100, "Сегодняшняя трата")

        expenses = get_expenses("today")
        today = datetime.now().strftime("%Y-%m-%d")

        # Хотя бы одна трата должна быть за сегодня
        today_expenses = [exp for exp in expenses if exp.date.startswith(today)]
        self.assertGreaterEqual(len(today_expenses), 1)

    def test_get_expenses_month(self):
        """Тест получения трат за месяц."""
        add_category("еда", "expense")
        add_expense("еда", -100, "Трата за месяц")

        expenses = get_expenses("month")
        current_month = datetime.now().strftime("%Y-%m")

        # Хотя бы одна трата должна быть за текущий месяц
        month_expenses = [exp for exp in expenses if exp.date.startswith(current_month)]
        self.assertGreaterEqual(len(month_expenses), 1)

    def test_add_category_success(self):
        """Тест успешного добавления новой категории."""
        success = add_category("развлечения", "expense")
        self.assertTrue(success)

        categories = get_categories()
        category_names = [cat.name for cat in categories]
        self.assertIn("развлечения", category_names)

    def test_add_category_duplicate(self):
        """Тест добавления дублирующей категории."""
        add_category("еда", "expense")

        # Перехватываем вывод для проверки сообщения об ошибке
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            success = add_category("еда", "expense")  # Пытаемся добавить дубликат

        self.assertFalse(success)
        output = f.getvalue()
        self.assertIn("Категория 'еда' уже существует", output)

    def test_add_category_invalid_type(self):
        """Тест добавления категории с неверным типом."""
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            success = add_category("тест", "неверный_тип")

        self.assertFalse(success)
        output = f.getvalue()
        self.assertIn("Ошибка: тип категории должен быть 'expense' или 'income'", output)

    def test_get_categories(self):
        """Тест получения списка категорий."""
        add_category("еда", "expense")
        add_category("зарплата", "income")

        categories = get_categories()
        self.assertEqual(len(categories), 2)

        category_names = [cat.name for cat in categories]
        self.assertIn("еда", category_names)
        self.assertIn("зарплата", category_names)


class TestReport(unittest.TestCase):
    """Тесты для генерации отчетов."""

    def setUp(self):
        """Настройка тестовых данных для отчетов."""
        self.test_dir = tempfile.mkdtemp()
        self.test_db_file = os.path.join(self.test_dir, "test_financial.db")

        # Патчим DATABASE_FILE для использования тестовой БД
        import fintracker.database
        self.original_db_file = fintracker.database.DATABASE_FILE
        fintracker.database.DATABASE_FILE = self.test_db_file

        # Инициализируем тестовую БД
        init_storage()

        # Добавляем тестовые категории
        add_category("еда", "expense")
        add_category("транспорт", "expense")
        add_category("зарплата", "income")

        # Добавляем тестовые операции с конкретными датами
        from fintracker.database import add_expense_to_db

        # Используем прямые вызовы к БД для установки конкретных дат
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO expenses (category, amount, description, date) VALUES (?, ?, ?, ?)',
                ("еда", -100, "Обед", "2025-01-15 12:00:00")
            )
            cursor.execute(
                'INSERT INTO expenses (category, amount, description, date) VALUES (?, ?, ?, ?)',
                ("еда", -150, "Ужин", "2025-01-15 19:00:00")
            )
            cursor.execute(
                'INSERT INTO expenses (category, amount, description, date) VALUES (?, ?, ?, ?)',
                ("транспорт", -50, "Такси", "2025-01-16 10:00:00")
            )
            cursor.execute(
                'INSERT INTO expenses (category, amount, description, date) VALUES (?, ?, ?, ?)',
                ("зарплата", 50000, "Зарплата", "2025-01-01 09:00:00")
            )
            conn.commit()
        finally:
            conn.close()

    def tearDown(self):
        """Очистка после тестов."""
        import fintracker.database
        fintracker.database.DATABASE_FILE = self.original_db_file

        if os.path.exists(self.test_db_file):
            os.unlink(self.test_db_file)
        shutil.rmtree(self.test_dir)

    def test_generate_category_report(self):
        """Тест генерации отчета по категориям."""
        report = generate_category_report("all")

        self.assertEqual(report["period"], "all")
        self.assertEqual(report["total_expenses"], 4)
        self.assertEqual(report["total_amount"], 50000 - 100 - 150 - 50)  # 49700

        # Проверяем что категории сгруппированы правильно
        categories_dict = dict(report["categories"])
        self.assertEqual(categories_dict["зарплата"], 50000)
        self.assertEqual(categories_dict["еда"], -250)
        self.assertEqual(categories_dict["транспорт"], -50)

    def test_generate_category_report_today(self):
        """Тест генерации отчета по категориям за сегодня."""
        # Добавляем операцию за сегодня
        add_category("еда", "expense")
        add_expense("еда", -75, "Сегодняшний обед")

        report = generate_category_report("today")
        self.assertEqual(report["period"], "today")
        # Должна быть хотя бы одна операция за сегодня
        self.assertGreaterEqual(report["total_expenses"], 1)

    def test_generate_period_report(self):
        """Тест генерации отчета за период."""
        report = generate_period_report("2025-01-15", "2025-01-15")

        self.assertEqual(report["period"], "2025-01-15 - 2025-01-15")
        self.assertEqual(report["total_expenses"], 2)  # Только траты на еду 15 числа
        self.assertEqual(report["total_amount"], -250)  # -100 + -150

    def test_generate_period_report_no_data(self):
        """Тест генерации отчета за период без данных."""
        report = generate_period_report("2020-01-01", "2020-01-02")

        self.assertEqual(report["period"], "2020-01-01 - 2020-01-02")
        self.assertEqual(report["total_expenses"], 0)
        self.assertEqual(report["total_amount"], 0)
        self.assertEqual(report["daily_totals"], {})

    def test_generate_category_report_with_output(self):
        """Тест отчета по категориям с выводом в файл."""
        output_file = os.path.join(self.test_dir, "test_report.csv")

        report = generate_category_report("all", output_file)

        self.assertTrue(os.path.exists(output_file))

        # Проверяем содержимое файла
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Финансовый отчет", content)
            self.assertIn("зарплата", content)
            self.assertIn("еда", content)

    def test_generate_period_report_with_output(self):
        """Тест отчета за период с выводом в файл."""
        output_file = os.path.join(self.test_dir, "test_period_report.csv")

        report = generate_period_report("2025-01-01", "2025-01-16", output_file)

        self.assertTrue(os.path.exists(output_file))

        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Финансовый отчет", content)
            self.assertIn("2025-01-01 - 2025-01-16", content)


class TestEdgeCases(unittest.TestCase):
    """Тесты граничных случаев и условий ошибок."""

    def setUp(self):
        """Настройка тестового окружения."""
        self.test_dir = tempfile.mkdtemp()
        self.test_db_file = os.path.join(self.test_dir, "test_financial.db")

        import fintracker.database
        self.original_db_file = fintracker.database.DATABASE_FILE
        fintracker.database.DATABASE_FILE = self.test_db_file

        init_storage()

    def tearDown(self):
        """Очистка после тестов."""
        import fintracker.database
        fintracker.database.DATABASE_FILE = self.original_db_file

        if os.path.exists(self.test_db_file):
            os.unlink(self.test_db_file)
        shutil.rmtree(self.test_dir)

    def test_empty_data_operations(self):
        """Тест операций с пустыми данными."""
        # Тест получения трат из пустой БД
        expenses = get_expenses("all")
        self.assertEqual(expenses, [])

        # Тест получения категорий из пустой БД
        categories = get_categories()
        self.assertEqual(categories, [])

        # Тест генерации отчета из пустых данных
        report = generate_category_report("all")
        self.assertEqual(report["total_expenses"], 0)
        self.assertEqual(report["total_amount"], 0)
        self.assertEqual(report["categories"], [])

    def test_expense_with_nonexistent_category(self):
        """Тест добавления операции с несуществующей категорией."""
        # В текущей реализации это допустимо, но проверим что не падает
        success = add_expense("несуществующая_категория", -100, "Тест")
        self.assertTrue(success)  # Должно работать даже без категории

        # Проверим что операция действительно добавилась
        expenses = get_expenses("all")
        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0].category, "несуществующая_категория")


class TestDatabaseIntegration(unittest.TestCase):
    """Тесты интеграции с базой данных."""

    def setUp(self):
        """Настройка тестовой БД."""
        self.test_dir = tempfile.mkdtemp()
        self.test_db_file = os.path.join(self.test_dir, "test_financial.db")

        import fintracker.database
        self.original_db_file = fintracker.database.DATABASE_FILE
        fintracker.database.DATABASE_FILE = self.test_db_file

        init_storage()

    def tearDown(self):
        """Очистка после тестов."""
        import fintracker.database
        fintracker.database.DATABASE_FILE = self.original_db_file

        if os.path.exists(self.test_db_file):
            os.unlink(self.test_db_file)
        shutil.rmtree(self.test_dir)

    def test_database_tables_created(self):
        """Тест что таблицы создаются правильно."""
        conn = get_connection()
        try:
            cursor = conn.cursor()

            # Проверяем существование таблицы categories
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categories'")
            categories_table = cursor.fetchone()
            self.assertIsNotNone(categories_table)

            # Проверяем существование таблицы expenses
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expenses'")
            expenses_table = cursor.fetchone()
            self.assertIsNotNone(expenses_table)

            # Проверяем структуру таблицы categories
            cursor.execute("PRAGMA table_info(categories)")
            categories_columns = {row[1]: row[2] for row in cursor.fetchall()}
            expected_categories_columns = ['id', 'name', 'type', 'created_at']
            for col in expected_categories_columns:
                self.assertIn(col, categories_columns)

            # Проверяем структуру таблицы expenses
            cursor.execute("PRAGMA table_info(expenses)")
            expenses_columns = {row[1]: row[2] for row in cursor.fetchall()}
            expected_expenses_columns = ['id', 'category', 'amount', 'description', 'date', 'created_at']
            for col in expected_expenses_columns:
                self.assertIn(col, expenses_columns)

        finally:
            conn.close()

    def test_data_persistence(self):
        """Тест сохранения данных между сессиями."""
        # Добавляем данные
        add_category("тест", "expense")
        add_expense("тест", -100, "Тестовая операция")

        # Пересоздаем соединение (имитируем перезапуск приложения)
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM categories")
            categories_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM expenses")
            expenses_count = cursor.fetchone()[0]

            self.assertEqual(categories_count, 1)
            self.assertEqual(expenses_count, 1)
        finally:
            conn.close()


if __name__ == '__main__':
    # Запускаем тесты
    unittest.main(verbosity=2)
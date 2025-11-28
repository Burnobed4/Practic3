"""
Модуль для работы с базой данных SQLite.
"""

import sqlite3
from typing import List, Dict, Any
from datetime import datetime

DATABASE_FILE = 'financial_tracker.db'


def get_connection():
    """Создает и возвращает соединение с базой данных."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Для доступа к колонкам по имени
    return conn


def init_database():
    """Инициализирует базу данных и создает таблицы если они не существуют."""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Создаем таблицу категорий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('expense', 'income')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Создаем таблицу операций
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category) REFERENCES categories (name)
            )
        ''')

        conn.commit()
        print("База данных инициализирована успешно")

    except sqlite3.Error as e:
        print(f"Ошибка инициализации базы данных: {e}")
        conn.rollback()
    finally:
        conn.close()


def add_category_to_db(name: str, category_type: str) -> bool:
    """
    Добавляет новую категорию в базу данных.

    Args:
        name: Название категории
        category_type: Тип категории ('expense' или 'income')

    Returns:
        bool: True если успешно, False если ошибка или дубликат
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO categories (name, type) VALUES (?, ?)',
            (name, category_type)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print(f"Категория '{name}' уже существует")
        return False
    except sqlite3.Error as e:
        print(f"Ошибка добавления категории: {e}")
        return False
    finally:
        conn.close()


def get_categories_from_db() -> List[Dict[str, Any]]:
    """
    Получает все категории из базы данных.

    Returns:
        List[Dict]: Список категорий
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT name, type FROM categories ORDER BY name')
        categories = [dict(row) for row in cursor.fetchall()]
        return categories
    except sqlite3.Error as e:
        print(f"Ошибка получения категорий: {e}")
        return []
    finally:
        conn.close()


def add_expense_to_db(category: str, amount: float, description: str = "") -> bool:
    """
    Добавляет новую операцию в базу данных.

    Args:
        category: Категория операции
        amount: Сумма операции
        description: Описание операции

    Returns:
        bool: True если успешно, False если ошибка
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO expenses (category, amount, description, date) VALUES (?, ?, ?, ?)',
            (category, amount, description, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Ошибка добавления операции: {e}")
        return False
    finally:
        conn.close()


def get_expenses_from_db(period: str = "all") -> List[Dict[str, Any]]:
    """
    Получает операции из базы данных за указанный период.

    Args:
        period: Период для фильтрации ('today', 'month', 'all')

    Returns:
        List[Dict]: Список операций
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        if period == "today":
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute(
                'SELECT category, amount, description, date FROM expenses WHERE date LIKE ? ORDER BY date DESC',
                (f'{today}%',)
            )
        elif period == "month":
            current_month = datetime.now().strftime('%Y-%m')
            cursor.execute(
                'SELECT category, amount, description, date FROM expenses WHERE date LIKE ? ORDER BY date DESC',
                (f'{current_month}%',)
            )
        else:  # all
            cursor.execute(
                'SELECT category, amount, description, date FROM expenses ORDER BY date DESC'
            )

        expenses = [dict(row) for row in cursor.fetchall()]
        return expenses

    except sqlite3.Error as e:
        print(f"Ошибка получения операций: {e}")
        return []
    finally:
        conn.close()


def get_category_report_from_db(period: str = "month") -> Dict[str, Any]:
    """
    Генерирует отчет по категориям из базы данных.

    Args:
        period: Период для отчета

    Returns:
        Dict: Данные отчета
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        if period == "today":
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute(
                'SELECT category, SUM(amount) as total FROM expenses WHERE date LIKE ? GROUP BY category ORDER BY total DESC',
                (f'{today}%',)
            )
        elif period == "month":
            current_month = datetime.now().strftime('%Y-%m')
            cursor.execute(
                'SELECT category, SUM(amount) as total FROM expenses WHERE date LIKE ? GROUP BY category ORDER BY total DESC',
                (f'{current_month}%',)
            )
        else:  # all
            cursor.execute(
                'SELECT category, SUM(amount) as total FROM expenses GROUP BY category ORDER BY total DESC'
            )

        categories_data = cursor.fetchall()

        # Получаем общее количество операций и сумму
        if period == "today":
            cursor.execute(
                'SELECT COUNT(*), SUM(amount) FROM expenses WHERE date LIKE ?',
                (f'{today}%',)
            )
        elif period == "month":
            cursor.execute(
                'SELECT COUNT(*), SUM(amount) FROM expenses WHERE date LIKE ?',
                (f'{current_month}%',)
            )
        else:
            cursor.execute('SELECT COUNT(*), SUM(amount) FROM expenses')

        count_result = cursor.fetchone()
        total_expenses = count_result[0] if count_result[0] else 0
        total_amount = count_result[1] if count_result[1] else 0

        report = {
            "period": period,
            "total_expenses": total_expenses,
            "total_amount": total_amount,
            "categories": [(row[0], row[1]) for row in categories_data],
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        return report

    except sqlite3.Error as e:
        print(f"Ошибка генерации отчета: {e}")
        return {
            "period": period,
            "total_expenses": 0,
            "total_amount": 0,
            "categories": [],
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    finally:
        conn.close()


def get_period_report_from_db(start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Генерирует отчет за период из базы данных.

    Args:
        start_date: Начальная дата (YYYY-MM-DD)
        end_date: Конечная дата (YYYY-MM-DD)

    Returns:
        Dict: Данные отчета
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Операции за период
        cursor.execute(
            '''SELECT category, amount, description, date 
               FROM expenses 
               WHERE date BETWEEN ? AND ? 
               ORDER BY date''',
            (f"{start_date} 00:00:00", f"{end_date} 23:59:59")
        )

        expenses_data = [dict(row) for row in cursor.fetchall()]

        # Суммы по дням
        cursor.execute(
            '''SELECT DATE(date) as day, SUM(amount) as daily_total 
               FROM expenses 
               WHERE date BETWEEN ? AND ? 
               GROUP BY DATE(date) 
               ORDER BY day''',
            (f"{start_date} 00:00:00", f"{end_date} 23:59:59")
        )

        daily_totals = {row[0]: row[1] for row in cursor.fetchall()}

        # Общая сумма всех операций за период
        total_amount = sum(expense['amount'] for expense in expenses_data)

        report = {
            "period": f"{start_date} - {end_date}",
            "total_expenses": len(expenses_data),
            "total_amount": total_amount,
            "daily_totals": daily_totals,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        return report

    except sqlite3.Error as e:
        print(f"Ошибка генерации отчета за период: {e}")
        return {
            "period": f"{start_date} - {end_date}",
            "total_expenses": 0,
            "total_amount": 0,
            "daily_totals": {},
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    finally:
        conn.close()
"""Модуль для работы с хранением данных.

Обеспечивает сохранение и загрузку финансовых данных из базы данных.
"""

from typing import List
from .models import Expense, Category
from .database import (
    add_expense_to_db,
    get_expenses_from_db,
    add_category_to_db,
    get_categories_from_db,
    init_database
)


def init_storage():
    """Инициализирует хранилище (базу данных)."""
    init_database()


def add_expense(category: str, amount: float, description: str = "") -> bool:
    """Добавляет новую финансовую операцию.

    Args:
        category (str): Категория операции.
        amount (float): Сумма операции.
        description (str, optional): Описание операции. По умолчанию "".

    Returns:
        bool: True если операция успешно добавлена, иначе False.
    """
    return add_expense_to_db(category, amount, description)


def get_expenses(period: str = "all") -> List[Expense]:
    """Получает список операций за указанный период.

    Args:
        period (str, optional): Период для фильтрации.
            Допустимые значения: 'today', 'month', 'all'. По умолчанию 'all'.

    Returns:
        List[Expense]: Список операций за указанный период.
    """
    expenses_data = get_expenses_from_db(period)
    return [Expense.from_dict(exp) for exp in expenses_data]


def get_categories() -> List[Category]:
    """Получает список всех категорий.

    Returns:
        List[Category]: Список объектов категорий.
    """
    categories_data = get_categories_from_db()
    return [Category.from_dict(cat) for cat in categories_data]


def add_category(name: str, cat_type: str) -> bool:
    """Добавляет новую категорию.

    Args:
        name (str): Название категории.
        cat_type (str): Тип категории ('expense' или 'income').

    Returns:
        bool: True если категория успешно добавлена, иначе False.

    Raises:
        ValueError: Если тип категории не 'expense' или 'income'.
    """
    if cat_type not in ["expense", "income"]:
        print(f"Ошибка: тип категории должен быть 'expense' или 'income', получено: '{cat_type}'")
        return False

    return add_category_to_db(name, cat_type)
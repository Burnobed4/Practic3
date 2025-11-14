"""Модуль для работы с хранением данных.

Обеспечивает сохранение и загрузку финансовых данных в JSON-файл.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
from .models import Expense, Category

DATA_FILE = 'data.json'


def load_data() -> Dict[str, Any]:
    """Загружает данные из JSON-файла.

    Returns:
        Dict[str, Any]: Словарь с данными приложения.

    Note:
        Если файл не существует, возвращает пустую структуру данных.
    """
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Ошибка загрузки данных: {e}")

    return {"expenses": [], "categories": []}


def save_data(data: Dict[str, Any]):
    """Сохраняет данные в JSON-файл.

    Args:
        data (Dict[str, Any]): Данные для сохранения.
    """
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"Ошибка сохранения данных: {e}")


def add_expense(category: str, amount: float, description: str = "") -> bool:
    """Добавляет новую финансовую операцию.

    Args:
        category (str): Категория операции.
        amount (float): Сумма операции.
        description (str, optional): Описание операции. По умолчанию "".

    Returns:
        bool: True если операция успешно добавлена, иначе False.
    """
    data = load_data()

    expense = Expense(category, amount, description)
    data["expenses"].append(expense.to_dict())

    save_data(data)
    return True


def get_expenses(period: str = "all") -> List[Dict]:
    """Получает список операций за указанный период.

    Args:
        period (str, optional): Период для фильтрации. 
            Допустимые значения: 'today', 'month', 'all'. По умолчанию 'all'.

    Returns:
        List[Dict]: Список операций за указанный период.
    """
    data = load_data()
    expenses = [Expense.from_dict(exp) for exp in data["expenses"]]

    if period == "today":
        today = datetime.now().strftime("%Y-%m-%d")
        return [exp for exp in expenses if exp.date.startswith(today)]
    elif period == "month":
        current_month = datetime.now().strftime("%Y-%m")
        return [exp for exp in expenses if exp.date.startswith(current_month)]
    else:
        return expenses


def get_categories() -> List[Category]:
    """Получает список всех категорий.

    Returns:
        List[Category]: Список объектов категорий.
    """
    data = load_data()
    return [Category.from_dict(cat) for cat in data.get("categories", [])]


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

    data = load_data()
    categories = [cat["name"] for cat in data.get("categories", [])]
    if name in categories:
        print(f"Категория '{name}' уже существует")
        return False

    category = Category(name, cat_type)
    data.setdefault("categories", []).append(category.to_dict())

    save_data(data)
    return True
"""Модуль с моделями данных для финансового трекера.

Содержит классы для представления категорий и финансовых операций.
"""

from datetime import datetime


class Category:
    """Класс для представления категории финансовых операций.

    Attributes:
        name (str): Название категории.
        type (str): Тип категории ('expense' или 'income').
    """

    def __init__(self, name: str, category_type: str):
        """Инициализирует категорию.

        Args:
            name (str): Название категории.
            category_type (str): Тип категории ('expense' или 'income').
        """
        self.name = name
        self.type = category_type

    def to_dict(self) -> dict:
        """Преобразует объект категории в словарь.

        Returns:
            dict: Словарь с данными категории.
        """
        return {"name": self.name, "type": self.type}

    @classmethod
    def from_dict(cls, data: dict) -> 'Category':
        """Создает объект категории из словаря.

        Args:
            data (dict): Словарь с данными категории.

        Returns:
            Category: Новый объект категории.
        """
        return cls(data["name"], data["type"])


class Expense:
    """Класс для представления финансовой операции.

    Attributes:
        category (str): Категория операции.
        amount (float): Сумма операции.
        description (str): Описание операции.
        date (str): Дата и время операции.
    """

    def __init__(self, category: str, amount: float, description: str = "", date: str = None):
        """Инициализирует финансовую операцию.

        Args:
            category (str): Категория операции.
            amount (float): Сумма операции.
            description (str, optional): Описание операции. По умолчанию "".
            date (str, optional): Дата операции. По умолчанию текущее время.
        """
        self.category = category
        self.amount = amount
        self.description = description
        self.date = date or datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self) -> dict:
        """Преобразует объект операции в словарь.

        Returns:
            dict: Словарь с данными операции.
        """
        return {
            "category": self.category,
            "amount": self.amount,
            "description": self.description,
            "date": self.date
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Expense':
        """Создает объект операции из словаря.

        Args:
            data (dict): Словарь с данными операции.

        Returns:
            Expense: Новый объект операции.
        """
        return cls(
            data['category'],
            data['amount'],
            data.get("description", ""),
            data.get("date")
        )
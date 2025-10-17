from datetime import datetime
from typing import Literal

class Category:
    def __init__(self, name: str, type: Literal['expense', 'income']):
        self.name = name
        self.type = type

    def to_dict(self):
        return {"name": self.name, "type": self.type}

    @classmethod
    def from_dict(cls,data):
        return cls(data['name'], data['type'])

class Expense:
    def __init__(self, category: str, amount: float,
                 description: str = "", date: str = None):
        self.category = category
        self.amount = amount
        self.description = description
        self.date = date or datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self):
        return {
            "category": self.category,
            "amount": self.amount,
            "description": self.description,
            "date": self.date
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data['category'],
            data['amount'],
            data.get['description', ""],
            data.get("date")
        )

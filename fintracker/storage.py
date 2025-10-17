import json
import os
from typing import List, Dict, Any
from .models import Expense, Category
import datetime

DATA_FILE = 'data.json'

def  load_data() -> Dict[str, Any]:
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Ошибка загрузки данных: {e}")

    return {"expenses": [], "categories": []}

def save_data(data: Dict[str, Any]):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"Ошибка сохранения данных: {e}")

def add_expense(category: str, amount: float, description: str = "") -> bool:
    data = load_data()

    expense = Expense(category,amount,description)
    data["expenses"].append(expense.to_dict())

    save_data(data)
    return True

def get_expenses(period: str = "all") -> List[Dict]:
    data = load_data()
    expenses = [Expense.from_dict(exp) for exp in data["expenses"]]

    if period == "today":
        today = datetime.now().strftime("%Y-%m-%d")
        return [exp for exp in expenses if exp.date.startswith(today)]
    elif period == "month":
        current_month = datetime.now().strftime("%Y-%m")
        return [exp for exp in expenses if exp.date.startswith(current_month)]

    return expenses

def get_categories() -> List[Category]:
    data = load_data()
    return [Category.from_dict(cat) for cat in data.get("categories", [])]

def add_category(name: str, type: str) -> bool:
    data = load_data()
    categories = [cat["name"] for cat in data.get("categories", [])]
    if name in categories:
        print(f"Категория '{name}' уже существует")
        return False

    category = Category(name, type)
    data.setdefault("categories", []).append(category.to_dict())

    save_data(data)
    return True

import logging
import math
import re
from datetime import datetime
from functools import reduce
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """Рассчитывает сумму для инвесткопилки через округление трат"""
    try:
        filter_by_month = lambda t: (datetime.strptime(t["Дата операции"], "%Y-%m-%d").strftime("%Y-%m") == month)

        calculate = lambda t: math.ceil(abs(t["Сумма операции"]) / limit) * limit - abs(t["Сумма операции"])

        contributions = map(calculate, filter(filter_by_month, transactions))
        return round(reduce(lambda a, b: a + b, contributions, 0.0), 2)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        return 0.0


def search_transactions(transactions: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Поиск транзакций по подстроке"""
    try:
        query = query.lower()
        return [
            t
            for t in transactions
            if query in str(t.get("Категория", "")).lower() or query in str(t.get("Описание", "")).lower()
        ]
    except Exception as e:
        logging.error(f"Ошибка поиска: {e}")
        return []


# Поиск переводов физлицам
PERSON_PATTERN = re.compile(r"\b[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.")


def find_person_transfers(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Поиск переводов физическим лицам"""
    return [
        t
        for t in transactions
        if t.get("Категория") == "Переводы" and PERSON_PATTERN.search(str(t.get("Описание", "")))
    ]

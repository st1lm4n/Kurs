import logging
import math
import re
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """
    Инвесткопилка
    """
    try:
        if limit not in {10, 50, 100}:
            raise ValueError("Недопустимый шаг округления")

        total = 0.0
        target_year, target_month = map(int, month.split("-"))

        for transaction in transactions:
            try:
                # Получаем дату из транзакции (уже в datetime формате)
                date = transaction["Дата операции"]

                # Проверяем совпадение месяца и года
                if date.year != target_year or date.month != target_month:
                    continue

                # Проверяем расходы (отрицательные суммы)
                amount = transaction["Сумма операции"]
                if amount >= 0:
                    continue

                # Расчет округления
                abs_amount = abs(amount)
                rounded = math.ceil(abs_amount / limit) * limit
                total += rounded - abs_amount

            except KeyError as e:
                logging.error(f"Отсутствует поле: {e}")

        return round(total, 2)

    except Exception as e:
        logging.error(f"Ошибка расчета: {e}")
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

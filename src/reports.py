import json
import logging
from datetime import datetime
from functools import wraps

import pandas as pd

logging.basicConfig(level=logging.INFO)


def report_to_file(filename=None):
    """Декоратор для отчетов"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Извлекаем имя файла, если оно передано
            custom_filename = kwargs.pop("filename", None) if "filename" in kwargs else None
            name = custom_filename or filename or f"{func.__name__}_{datetime.now().strftime('%Y%m%d')}.json"

            # Выполняем функцию
            result = func(*args, **kwargs)

            # Сохраняем результат в файл
            try:
                if isinstance(result, dict):
                    # Преобразуем словарь в список для сохранения в JSON
                    result_list = [{"Месяц": k, "Сумма": v} for k, v in result.items()]
                    with open(name, "w", encoding="utf-8") as f:
                        json.dump(result_list, f, ensure_ascii=False, indent=4)
                else:
                    # Если результат не словарь, сохраняем как есть
                    pd.DataFrame(result).to_json(name, orient="records")
                logging.info(f"Отчет сохранен в файл: {name}")
            except Exception as e:
                logging.error(f"Ошибка сохранения отчета: {e}")
            return result

        return wrapper

    return decorator


@report_to_file()
def category_spending(df: pd.DataFrame, category: str, date: str = None, **kwargs) -> dict:
    """Анализ трат по категории за последние 3 месяца"""
    try:
        # Преобразуем дату в datetime
        date = pd.to_datetime(date or datetime.now())
        start_date = date - pd.DateOffset(months=3)

        # Фильтрация данных
        filtered = df[(df["Категория"] == category) & (df["Дата"] >= start_date) & (df["Дата"] <= date)]

        # Группировка по месяцам и суммирование
        result = filtered.groupby(pd.Grouper(key="Дата", freq="ME"))["Сумма"].sum().to_dict()

        # Преобразуем ключи в строки для JSON
        return {k.strftime("%Y-%m"): v for k, v in result.items()}
    except Exception as e:
        logging.error(f"Ошибка анализа трат: {e}")
        return {}

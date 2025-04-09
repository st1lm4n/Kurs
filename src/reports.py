# reports.py
import logging
from datetime import datetime
from functools import wraps
from typing import Optional

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def report_to_file(filename=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Выделяем filename из kwargs
                custom_filename = kwargs.pop('filename', None)
                file_name = custom_filename or filename or f"{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

                result = func(*args, **kwargs)

                if isinstance(result, pd.DataFrame):
                    result.to_json(file_name, orient="records", indent=4, force_ascii=False)
                    logging.info(f"Отчет сохранен в файл: {file_name}")

                return result

            except Exception as e:
                logging.error(f"Ошибка сохранения: {e}")
                raise

        return wrapper

    return decorator


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    try:
        # Преобразование столбца 'Дата платежа'
        transactions["Дата платежа"] = pd.to_datetime(transactions["Дата платежа"], format="%d.%m.%Y")

        # Преобразование даты отчета
        current_date = pd.to_datetime(date) if date else datetime.now()
        start_date = current_date - pd.DateOffset(months=3)

        # Фильтрация данных
        filtered = transactions[
            (transactions["Категория"] == category) &
            (transactions["Дата платежа"] >= start_date) &
            (transactions["Дата платежа"] <= current_date)
            ]

        # Группировка по месяцам
        result = filtered.groupby(pd.Grouper(key="Дата платежа", freq="ME"))["Сумма платежа"].sum().reset_index()

        # Заполнение отсутствующих месяцев нулями
        all_months = pd.date_range(start=start_date, end=current_date, freq="ME")
        result = result.set_index("Дата платежа").reindex(all_months, fill_value=0).reset_index()

        # Форматирование результата
        result = result.rename(columns={"index": "Месяц", "Сумма платежа": "Сумма"})
        result["Месяц"] = result["Месяц"].dt.strftime("%Y-%m")

        return result

    except Exception as e:
        logging.error(f"Ошибка анализа данных: {e}")
        return pd.DataFrame(columns=["Месяц", "Сумма"])

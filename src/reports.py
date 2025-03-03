# reports.py
import logging
from datetime import datetime
from functools import wraps
from typing import Optional

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def report_to_file(filename=None):
    """Декоратор для сохранения отчетов в JSON файл"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Вызываем оригинальную функцию
                result = func(*args, **kwargs)

                # Генерируем имя файла
                file_name = filename or f"{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

                # Сохраняем результат
                if isinstance(result, pd.DataFrame):
                    result.to_json(file_name, orient="records", indent=4, force_ascii=False)
                    logging.info(f"Отчет сохранен в файл: {file_name}")

                return result

            except Exception as e:
                logging.error(f"Ошибка при сохранении отчета: {e}")
                raise

        return wrapper

    return decorator


@report_to_file()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Анализ трат по категории за последние 3 месяца
    """
    try:
        # Проверка наличия обязательных колонок
        required_columns = ["Дата платежа", "Категория", "Сумма платежа"]
        if not all(col in transactions.columns for col in required_columns):
            raise ValueError("Отсутствуют обязательные колонки в данных")

        # Преобразование столбца 'Дата платежа'
        transactions["Дата платежа"] = pd.to_datetime(transactions["Дата платежа"], format="%d.%m.%Y")

        # Преобразование даты отчета
        current_date = pd.to_datetime(date) if date else datetime.now()
        start_date = current_date - pd.DateOffset(months=3)

        # Фильтрация данных
        filtered = transactions[
            (transactions["Категория"] == category)
            & (transactions["Дата платежа"] >= start_date)
            & (transactions["Дата платежа"] <= current_date)
        ]

        # Отладочная печать
        print(f"Найдено транзакций после фильтрации: {len(filtered)}")

        # Группировка по месяцам
        result = filtered.groupby(pd.Grouper(key="Дата платежа", freq="ME"))["Сумма платежа"].sum().reset_index()

        # Форматирование результата
        result = result.rename(columns={"Дата платежа": "Месяц", "Сумма платежа": "Сумма"})
        result["Месяц"] = result["Месяц"].dt.strftime("%Y-%m")

        return result

    except Exception as e:
        logging.error(f"Ошибка анализа данных: {e}")
        return pd.DataFrame(columns=["Месяц", "Сумма"])

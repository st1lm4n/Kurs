# views.py
import json
import logging
import os
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv

from src.utils import get_currency_rates, get_stock_prices

load_dotenv()
API_KEY = os.getenv("API_KEY")

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def load_user_settings():
    """Загрузка пользовательских настроек"""
    try:
        with open("..//user_settings.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        logging.error(f"Ошибка загрузки user_settings.json: {e}")
        return {"user_currencies": [], "user_stocks": []}


def get_greeting():
    """Определение приветствия"""
    now = datetime.now()
    hour = now.hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_data_by_period(df: pd.DataFrame, date_time_str: str) -> pd.DataFrame:
    """Фильтрация данных по периоду (с начала месяца до указанной даты)"""
    try:
        input_date = datetime.strptime(date_time_str, "%Y-%m-%d")
        start_of_month = input_date.replace(day=1)

        # Фильтрация данных за период
        mask = (df["Дата платежа"] >= start_of_month) & (df["Дата платежа"] <= input_date)
        return df.loc[mask]
    except Exception as e:
        logging.error(f"Ошибка фильтрации данных по периоду: {e}")
        return pd.DataFrame()


def get_card_data(df: pd.DataFrame) -> list:
    """Извлечение данных о картах (только расходы)"""
    try:
        # Фильтрация только расходных операций
        df_expenses = df[df["Сумма платежа"] < 0]

        # Группировка и агрегация
        card_data = (
            df_expenses.groupby("Номер карты")
            .agg(
                total_spent=("Сумма платежа", lambda x: abs(x).sum()),
                cashback=("Кэшбэк", "sum")
            )
            .reset_index()
        )

        # Форматирование результата
        card_data["last_digits"] = card_data["Номер карты"].str[-4:]
        return card_data[["last_digits", "total_spent", "cashback"]].to_dict("records")
    except Exception as e:
        logging.error(f"Ошибка обработки данных о картах: {e}")
        return []


def get_top_transactions(df: pd.DataFrame) -> list:
    """Извлечение топ-5 транзакций (только расходы)"""
    try:
        # Фильтрация только расходных операций
        df_expenses = df[df["Сумма платежа"] < 0]

        # Сортировка и выбор топ-5
        top_5 = df_expenses.nlargest(5, "Сумма платежа")

        # Форматирование результата
        top_5["date"] = top_5["Дата платежа"].dt.strftime("%d.%m.%Y")
        return top_5.rename(columns={
            "Сумма платежа": "amount",
            "Категория": "category",
            "Описание": "description"
        })[["date", "amount", "category", "description"]].to_dict("records")
    except Exception as e:
        logging.error(f"Ошибка обработки транзакций: {e}")
        return []


def generate_response(date_time_str: str) -> dict:
    """Главная функция"""
    try:
        # Загрузка и подготовка данных
        df = pd.read_excel("..//data/operations.xlsx", sheet_name="Отчет по операциям")
        df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], format="%d.%m.%Y")

        # Фильтрация данных по периоду
        filtered_df = get_data_by_period(df, date_time_str)

        # Загрузка настроек
        settings = load_user_settings()
        user_currencies = settings.get("user_currencies", [])
        user_stocks = settings.get("user_stocks", [])

        # Формирование ответа
        return {
            "greeting": get_greeting(),
            "cards": get_card_data(filtered_df),
            "top_transactions": get_top_transactions(filtered_df),
            "currency_rates": get_currency_rates(user_currencies),
            "stock_prices": get_stock_prices(user_stocks)
        }
    except Exception as e:
        logging.error(f"Ошибка генерации ответа: {e}")
        return {"error": "Произошла ошибка при генерации ответа"}
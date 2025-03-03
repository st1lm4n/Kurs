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
        with open("user_settings.json", "r", encoding="utf-8") as file:
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


def get_card_data():
    """Извлечение данных о картах из Excel"""
    try:
        # Чтение данных из файла
        df = pd.read_excel("data/operations.xlsx", sheet_name="Отчет по операциям")

        # Группировка по номеру карты и расчет общей суммы и кэшбэка
        card_data = (
            df.groupby("Номер карты")
            .agg(total_spent=("Сумма операции", lambda x: abs(x).sum()), cashback=("Бонусы (включая кэшбэк)", "sum"))
            .reset_index()
        )

        # Преобразование данных в нужный формат
        card_data["last_digits"] = card_data["Номер карты"].str[-4:]
        card_data = card_data[["last_digits", "total_spent", "cashback"]].to_dict("records")

        return card_data
    except Exception as e:
        logging.error(f"Ошибка чтения данных о картах: {e}")
        return []


def get_top_transactions(date_time_str):
    """Извлечение топ-5 транзакций из Excel"""
    try:
        # Преобразуем входную дату в datetime
        input_date = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
        start_of_month = input_date.replace(day=1)

        # Чтение данных из файла
        df = pd.read_excel("data/operations.xlsx", sheet_name="Отчет по операциям")

        # Преобразование столбца "Дата операции" в datetime
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

        # Фильтрация данных за период
        mask = (df["Дата операции"] >= start_of_month) & (df["Дата операции"] <= input_date)
        filtered_transactions = df.loc[mask]

        # Сортировка по сумме и выбор топ-5
        top_5 = filtered_transactions.nlargest(5, "Сумма операции")

        # Преобразование данных в нужный формат
        top_5["date"] = top_5["Дата операции"].dt.strftime("%d.%m.%Y")
        top_5 = top_5.rename(columns={"Сумма операции": "amount", "Категория": "category", "Описание": "description"})

        return top_5[["date", "amount", "category", "description"]].to_dict("records")
    except Exception as e:
        logging.error(f"Ошибка чтения транзакций: {e}")
        return []


def generate_response(date_time_str):
    """Главная функция"""
    try:
        # Загрузка настроек
        settings = load_user_settings()
        user_currencies = settings.get("user_currencies", [])
        user_stocks = settings.get("user_stocks", [])

        # Определение приветствия
        greeting = get_greeting()

        # Получение данных о курсах валют и акциях
        currency_rates = get_currency_rates(user_currencies)
        stock_prices = get_stock_prices(user_stocks)

        # Извлечение данных о картах и транзакциях
        cards = get_card_data()
        top_transactions = get_top_transactions(date_time_str)

        # Формирование JSON-ответа
        response = {
            "greeting": greeting,
            "cards": cards,
            "top_transactions": top_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices,
        }

        return response

    except Exception as e:
        logging.error(f"Ошибка генерации ответа: {e}")
        return {"error": "Произошла ошибка при генерации ответа"}

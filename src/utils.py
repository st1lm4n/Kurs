import logging
import os
from typing import Any, Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")


def load_transactions(filepath: str) -> List[Dict[str, Any]]:
    """Загрузка транзакций из Excel"""
    df = pd.read_excel(filepath, parse_dates=["Дата операции"])
    return df.to_dict("records")


def get_currency_rates(currencies):
    """Получение курсов валют"""
    rates = []
    for currency in currencies:
        try:
            response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{currency}")
            data = response.json()
            rates.append({"currency": currency, "rate": data["rates"]["RUB"]})
        except Exception as e:
            logging.error(f"Ошибка получения курса валюты {currency}: {e}")
    return rates


def get_stock_prices(stocks):
    """Получение цен на акции"""
    prices = []
    for stock in stocks:
        try:
            response = requests.get(
                f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={API_KEY}"
            )
            data = response.json()
            prices.append({"stock": stock, "price": float(data["Global Quote"]["05. price"])})
        except Exception as e:
            logging.error(f"Ошибка получения цены акции {stock}: {e}")
    return prices

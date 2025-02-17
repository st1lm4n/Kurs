# test_views.py
import json
from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.views import (generate_response, get_card_data, get_currency_rates, get_greeting, get_top_transactions,
                       load_user_settings)


# Фикстуры для тестовых данных
@pytest.fixture
def sample_user_settings(tmp_path):
    data = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "TSLA"]}
    file_path = tmp_path / "..//user_settings.json"
    with open(file_path, "w") as f:
        json.dump(data, f)
    return file_path


@pytest.fixture
def sample_excel_file(tmp_path):
    data = {
        "Дата операции": ["31.12.2021 16:44:00", "31.12.2021 01:23:42"],
        "Номер карты": ["*7197", "*5091"],
        "Сумма операции": [-160.89, -564],
        "Бонусы (включая кэшбэк)": [3, 5],
        "Категория": ["Супермаркеты", "Различные товары"],
        "Описание": ["Колхоз", ""],
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "..//operations.xlsx"
    df.to_excel(file_path, sheet_name="Отчет по операциям", index=False)
    return file_path


# Тесты для load_user_settings
def test_load_user_settings_valid(sample_user_settings):
    with patch("src.open", create=True) as mock_open:
        result = load_user_settings()
    assert result["user_currencies"] == ["USD", "EUR"]


def test_load_user_settings_missing_file():
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = load_user_settings()
    assert result == {"user_currencies": [], "user_stocks": []}


# Тесты для get_greeting
@patch("src.views.datetime")
def test_get_greeting_morning(mock_datetime):
    mock_datetime.now.return_value = datetime(2023, 1, 1, 7, 0, 0)
    assert get_greeting() == "Доброе утро"


@patch("src.views.datetime")
def test_get_greeting_night(mock_datetime):
    mock_datetime.now.return_value = datetime(2023, 1, 1, 3, 0, 0)
    assert get_greeting() == "Доброй ночи"


# Тесты для get_currency_rates
@patch("src.views.requests.get")
def test_get_currency_rates_success(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {"rates": {"RUB": 75.5}}
    mock_get.return_value = mock_response

    result = get_currency_rates(["USD"])
    assert result == [{"currency": "USD", "rate": 75.5}]


# Тесты для get_card_data
def test_get_card_data(sample_excel_file):
    with patch("src.views.pd.read_excel") as mock_read:
        mock_read.return_value = pd.read_excel(sample_excel_file)
        result = get_card_data()

    assert len(result) == 0


# Тесты для get_top_transactions
def test_get_top_transactions(sample_excel_file):
    test_date = "2021-12-31 23:59:59"

    with patch("src.views.pd.read_excel") as mock_read:
        mock_read.return_value = pd.read_excel(sample_excel_file)
        result = get_top_transactions(test_date)

    assert len(result) == 0


# Тесты для generate_response
@patch("src.views.get_currency_rates")
@patch("src.views.get_stock_prices")
def test_generate_response_success(mock_stocks, mock_currencies, sample_user_settings, sample_excel_file):
    mock_currencies.return_value = [{"currency": "USD", "rate": 75.5}]
    mock_stocks.return_value = [{"stock": "AAPL", "price": 150.0}]

    with patch("src.views.load_user_settings") as mock_settings:
        mock_settings.return_value = json.load(open(sample_user_settings))
        response = generate_response("2021-12-31 23:59:59")

    assert "greeting" in response
    assert len(response["cards"]) == 7
    assert response["currency_rates"][0]["rate"] == 75.5

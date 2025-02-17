import pytest

from src.services import investment_bank, search_transactions


def test_basic_case():
    transactions = [
        {"Дата операции": "2023-10-15", "Сумма операции": 1712},
        {"Дата операции": "2023-10-16", "Сумма операции": -160.89},
        {"Дата операции": "2023-11-01", "Сумма операции": 100},
    ]
    assert investment_bank("2023-10", transactions, 50) == 77.11
    assert investment_bank("2023-11", transactions, 10) == 0.0


def test_edge_cases():
    transactions = [
        {"Дата операции": "2023-10-15", "Сумма операции": 200},
        {"Дата операции": "2023-10-16", "Сумма операции": 149.99},
    ]
    assert investment_bank("2023-10", transactions, 50) == 0.01


def test_invalid_data():
    # Неверный формат даты
    assert investment_bank("2023-13", [{"Дата операции": "2023-13-01"}], 10) == 0.0

    # Отсутствует поле суммы
    assert investment_bank("2023-10", [{"Дата операции": "2023-10-01"}], 10) == 0.0


@pytest.fixture
def sample_transactions():
    return [
        {"Категория": "Супермаркеты", "Описание": "Пятерочка", "Сумма": 500},
        {"Категория": "Кафе", "Описание": "Starbucks", "Сумма": 300},
        {"Категория": "Транспорт", "Описание": "Uber", "Сумма": 200},
        {"Категория": None, "Описание": "Перевод", "Сумма": 1000},
    ]


def test_basic_search(sample_transactions):
    result = search_transactions(sample_transactions, "пятерочка")  # Исправлен запрос
    assert len(result) == 1
    assert result[0]["Категория"] == "Супермаркеты"


def test_case_insensitive(sample_transactions):
    result = search_transactions(sample_transactions, "UBER")
    assert len(result) == 1
    assert result[0]["Описание"].lower() == "uber"  # Проверка в нижнем регистре


def test_no_matches(sample_transactions):
    assert len(search_transactions(sample_transactions, "аптека")) == 0


def test_data_invalid():
    assert search_transactions([{"wrong_field": 123}], "test") == []


def test_search_transactions(sample_transactions):
    result = search_transactions(sample_transactions, "перевод")
    assert len(result) == 1

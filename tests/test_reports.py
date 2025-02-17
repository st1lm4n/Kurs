# test_reports.py

import pandas as pd
import pytest

from src.reports import category_spending


@pytest.fixture
def sample_dataframe():
    """Фикстура с тестовыми данными"""
    return pd.DataFrame(
        {
            "Дата": pd.date_range(start="2023-01-01", periods=180, freq="D"),
            "Категория": ["Еда"] * 90 + ["Транспорт"] * 90,
            "Сумма": [100] * 180,
        }
    )


def test_basic_functionality(sample_dataframe):
    # Тест базового функционала
    result = category_spending(sample_dataframe, "Еда", "2023-06-15")

    # Проверка структуры результата
    assert isinstance(result, dict)
    assert len(result) == 1  # Апрель, май, июнь
    assert all(len(k) == 7 and k.count("-") == 1 for k in result.keys())  # Формат YYYY-MM


def test_edge_cases(sample_dataframe):
    # Тест с несуществующей категорией
    assert category_spending(sample_dataframe, "Развлечения") == {}

    # Тест с пустым DataFrame
    assert category_spending(pd.DataFrame(), "Еда") == {}


def test_error_handling(caplog):
    # Тест обработки ошибок с некорректными данными
    invalid_df = pd.DataFrame({"Wrong_Column": [1]})
    result = category_spending(invalid_df, "Еда")

    # Проверка возвращаемого значения
    assert result == {}

    # Проверка записи в лог
    assert "Ошибка анализа трат" in caplog.text


def test_month_grouping():
    # Тест точной группировки по месяцам
    test_data = pd.DataFrame(
        {
            "Дата": ["2023-03-31", "2023-04-01", "2023-05-15", "2023-06-30"],
            "Категория": ["Тест"] * 4,
            "Сумма": [100] * 4,
        }
    )
    test_data["Дата"] = pd.to_datetime(test_data["Дата"])

    result = category_spending(test_data, "Тест", "2023-06-30")

    # Проверка группировки
    assert len(result) == 4
    assert "2023-04" in result  # Апрель должен попасть в отчет

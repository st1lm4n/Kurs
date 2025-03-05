# test_reports.py
import json
import os

import pandas as pd
import pytest

from src.reports import report_to_file, spending_by_category


@pytest.fixture
def sample_data():
    return pd.DataFrame(
        {
            "Дата платежа": ["01.01.2023", "15.01.2023", "01.02.2023", "15.03.2023", "01.04.2023"],
            "Категория": ["Еда", "Еда", "Транспорт", "Еда", "Развлечения"],
            "Сумма платежа": [1000, 1500, 500, 2000, 3000],
        }
    )


def test_spending_by_category_basic(sample_data):
    # Тест базового сценария
    result = spending_by_category(sample_data, "Еда", "2023-04-01")
    expected = pd.DataFrame({"Месяц": ["2023-01", "2023-02", "2023-03"], "Сумма": [2500, 0, 2000]})
    pd.testing.assert_frame_equal(result, expected)





def test_spending_by_category_missing_columns():
    # Тест отсутствия обязательных колонок
    invalid_data = pd.DataFrame({"Date": [], "Category": [], "Amount": []})
    result = spending_by_category(invalid_data, "Еда")
    assert result.empty


def test_report_to_file_decorator(sample_data, tmp_path):
    # Тест декоратора сохранения в файл
    filename = tmp_path / "test_report.json"

    @report_to_file(filename=filename)
    def test_func():
        return sample_data

    # Вызываем декорированную функцию
    result = test_func()

    # Проверяем создание файла
    assert os.path.exists(filename)

    # Проверяем содержимое файла
    with open(filename, "r") as f:
        content = json.load(f)
        assert len(content) == 5


def test_price_formatting(sample_data):
    # Тест форматирования цен
    result = spending_by_category(sample_data, "Еда")
    assert all(result["Сумма"] >= 0)
    assert all(len(month) == 7 for month in result["Месяц"])  # Формат ГГГГ-ММ




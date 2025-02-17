from datetime import datetime

import pandas as pd
import pytest

from src.utils import load_transactions


@pytest.fixture
def sample_excel_file(tmp_path):
    """Фикстура для создания временного Excel-файла с тестовыми данными"""
    data = {
        "Дата операции": [datetime(2023, 10, 1), datetime(2023, 10, 2)],
        "Категория": ["Еда", "Транспорт"],
        "Сумма": [100, 200],
    }
    df = pd.DataFrame(data)
    filepath = tmp_path / "test_transactions.xlsx"
    df.to_excel(filepath, index=False)
    return filepath


def test_load_transactions_valid_file(sample_excel_file):
    """Тест загрузки корректного Excel-файла"""
    result = load_transactions(sample_excel_file)

    # Проверка структуры результата
    assert isinstance(result, list)
    assert len(result) == 2

    # Проверка содержимого
    assert result[0]["Дата операции"] == datetime(2023, 10, 1)
    assert result[0]["Категория"] == "Еда"
    assert result[0]["Сумма"] == 100


def test_load_transactions_invalid_file(tmp_path):
    """Тест загрузки несуществующего файла"""
    invalid_file = tmp_path / "nonexistent.xlsx"
    with pytest.raises(FileNotFoundError):
        load_transactions(invalid_file)


def test_load_transactions_empty_file(tmp_path):
    """Тест загрузки пустого Excel-файла"""
    empty_file = tmp_path / "empty.xlsx"
    pd.DataFrame().to_excel(empty_file, index=False)

    result = load_transactions(empty_file)
    assert isinstance(result, list)
    assert len(result) == 0


def test_load_transactions_invalid_date_format(tmp_path):
    """Тест загрузки файла с некорректным форматом даты"""
    data = {
        "Дата операции": ["2023-10-01", "2023-10-02"],  # Даты как строки
        "Категория": ["Еда", "Транспорт"],
        "Сумма": [100, 200],
    }
    df = pd.DataFrame(data)
    filepath = tmp_path / "invalid_date_format.xlsx"
    df.to_excel(filepath, index=False)

    result = load_transactions(filepath)
    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0]["Дата операции"], datetime)  # Проверка, что даты преобразованы

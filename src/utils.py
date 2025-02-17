from typing import Any, Dict, List

import pandas as pd


def load_transactions(filepath: str) -> List[Dict[str, Any]]:
    """Загрузка транзакций из Excel"""
    df = pd.read_excel(filepath, parse_dates=["Дата операции"])
    return df.to_dict("records")

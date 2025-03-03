# main.py
import json

import pandas as pd

from src.reports import spending_by_category
from src.services import find_person_transfers, investment_bank, search_transactions
from utils import load_transactions
from views import generate_response, get_greeting


def print_menu():
    """Выводит меню доступных функций"""
    print("\n" + "=" * 50)
    print(f"{get_greeting()}, выберите действие:")
    print("1. Сгенерировать полный отчет для веб-страницы")
    print("2. Рассчитать сумму для инвесткопилки")
    print("3. Поиск транзакций по ключевым словам")
    print("4. Найти переводы физическим лицам")
    print("5. Сформировать отчет по тратам за 3 месяца")
    print("6. Выход")
    print("=" * 50 + "\n")


def main():
    # Загрузка данных
    try:
        transactions = load_transactions("..//data/operations.xlsx")
        df = pd.read_excel("..//data/operations.xlsx", parse_dates=["Дата платежа"])
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return

    while True:
        print_menu()
        choice = input("Введите номер действия: ")

        if choice == "1":
            # Генерация веб-отчета
            date_str = input("Введите дату и время (формат: ГГГГ-ММ-ДД ЧЧ:ММ:СС): ")
            try:
                report = generate_response(date_str)
                with open("web_report.json", "w", encoding="utf-8") as f:
                    json.dump(report, f, ensure_ascii=False, indent=4)
                print("Отчет сохранен в web_report.json")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "2":
            # Инвесткопилка
            month = input("Введите месяц (формат: ГГГГ-ММ): ")
            limit = int(input("Введите шаг округления (10/50/100): "))
            try:
                result = investment_bank(month, transactions, limit)
                print(f"Сумма для инвесткопилки: {result:.2f} ₽")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "3":
            # Поиск транзакций
            query = input("Введите поисковый запрос: ")
            results = search_transactions(transactions, query)
            print(f"Найдено транзакций: {len(results)}")
            for idx, t in enumerate(results[:5], 1):
                print(f"{idx}. {t.get('Описание', '')} - {t.get('Сумма операции', 0)} ₽")

        elif choice == "4":
            # Переводы физлицам
            results = find_person_transfers(transactions)
            print(f"Найдено переводов: {len(results)}")
            for idx, t in enumerate(results[:5], 1):
                print(f"{idx}. {t.get('Описание', '')} - {t.get('Сумма операции', 0)} ₽")

        elif choice == "5":

            # Отчет по тратам

            category = input("Введите категорию: ").strip()  # Удаляем пробелы

            date_input = input("Введите дату (формат: ГГГГ-ММ-ДД) или оставьте пустым: ").strip()

            try:

                # Преобразование даты

                date = pd.to_datetime(date_input) if date_input else None

                result = spending_by_category(df, category, date)

                if not result.empty:

                    print("\nОтчет по месяцам:")

                    for _, row in result.iterrows():
                        print(f"{row['Месяц']}: {row['Сумма']:.2f} ₽")

                else:

                    print("\nНет данных для отчета. Проверьте:")

                    print("- Правильность категории")

                    print("- Наличие транзакций за последние 3 месяца")

            except Exception as e:

                print(f"\nОшибка: {e}")

        elif choice == "6":
            print("Выход из программы...")
            break

        else:
            print("Некорректный ввод! Попробуйте снова.")

        input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    main()

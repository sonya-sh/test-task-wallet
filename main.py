import json
from typing import Dict, List, Tuple
from datetime import datetime

# Функция, обрабатывающая корректный ввод даты.
def get_date_input(prompt: str = None, error_message: str = "Дата не может быть пустой.") -> str:
    while True:
        date_str = input(prompt)
        if date_str:
            try:
                datetime.strptime(date_str, '%d-%m-%Y')
                return date_str
            except ValueError as e:
                if (f"time data '{date_str}' does not match format '%d-%m-%Y'") in str(e):
                    print("Дата должна быть в формате дд-мм-гггг")
        else:
            print(error_message)

# Функция, обрабатывающая корректный ввод категории.
def get_category_input(prompt: str = None, error_message: str = "Некорректная категория. Введите 'Доход' или 'Расход'.") -> str:
    while True:
        category = input(prompt)
        if category in ("Доход", "Расход"):
            return category
        else:
            print(error_message)

# Функция, обрабатывающая корректный ввод суммы.
def get_summ_input(prompt: str = None, error_message: str = "Значение должно быть числом") -> str:
    while True:
        try:
            value = float(input(prompt))
            if value < 0:
                raise ValueError("Значение не может быть отрицательным.")
            return str(value)
        except ValueError as e:
            if "could not convert string to float" in str(e):
                print(error_message)
            else:
                print(e)

# Функция для получения словаря с данными добавляемой записи.
# Применяется для метода add_entry
def get_entry_data_for_add_entry() -> Dict[str, str]:
    entry_data: Dict[str, str] = {}

    entry_data["Дата"] = get_date_input("Введите дату в формате дд-мм-ггг: ")
    entry_data["Категория"] = get_category_input("Введите категорию (Доход/Расход): ")
    entry_data["Сумма"] = get_summ_input("Введите сумму: ")
    entry_data["Описание"] = input("Введите описание: ")

    return entry_data
    
# Функция для получния id записи, которую нужно отредактировать, а также 
# пар ключ-значение, представляющих поля и новые значения для редактирования.
# Применяется для метода edit_entry
def get_id_and_kwargs_for_edit_entry() -> Tuple[str, Dict[str, str]]:

    entry_id: str = input("Введите ID записи, которую хотите отредактировать: ")
    fields_to_edit: List[str] = input("Введите поле для редактирования, или несколько полей через пробел (например: Сумма Дата): ").strip().split(' ')
    new_values: Dict[str, str] = {}

    # Словарь с полями, которые нужно проверять на корректность (значения - соответствующие проверяющие функции)
    input_functions = {
        "Дата": get_date_input,
        "Категория": get_category_input,
        "Сумма": get_summ_input,
    }

    for field in fields_to_edit:
        input_function = input_functions.get(field, input)  # Если для поля нет специальной функции, используется input
        new_value = input_function(f"Введите новое значение для поля '{field}': ")
        new_values[field] = new_value

    return entry_id, new_values
    
# Функция для получния пар ключ-значение, представляющих поля и их значения для поиска записей.
# Применяется для search_entry
def get_kwargs_for_search_entry() -> Dict[str, str]:
    
    keys_for_search: List[str] = input("Введите поле для поиска, или несколько полей через пробел (например: Дата, Категория): ").strip().split(' ')
    kwargs: Dict[str, str] = {}

    input_functions = {
        "Дата": get_date_input,
        "Категория": get_category_input,
        "Сумма": get_summ_input,
    }

    for key in keys_for_search:
        input_function = input_functions.get(key, input)  # Если для поля нет специальной функции, используется input
        value_for_key_for_search = input_function(f"Введите значение для поля '{key}' поиска: ")
        kwargs[key] = value_for_key_for_search

    return kwargs
    
# Вывод словаря записей. 
# Применяется для вывода результатов search_entry
def print_results(results: Dict[str, Dict[str, str]]) -> None:
    print('\n')
    for entry_id, entry_data in results.items():
        print(f"{entry_id}: ")
        for key, value in entry_data.items():
            print(f"    {key}: {value}")
        print(" ")


class Wallet:

    def __init__(self, file_path):
        self.file_path = file_path

    # 1. Вывод баланса: Показать текущий баланс, а также отдельно доходы и расходы.
    def show_balance(self) -> None:

        total_balance, total_income, total_expense = self.get_balance()
        print(f"Общий баланс: {total_balance}")
        print(f"Сумма доходов: {total_income}")
        print(f"Сумма расходов: {total_expense}")

    # 2. Добавление новой записи о доходе или расходе.
    def add_entry(self, entry_data: Dict[str, str]) -> None:

        with open(self.file_path, 'r+') as file:
            try:
                data: Dict[str, Dict[str, str]] = json.load(file)
            except json.JSONDecodeError:
                raise ValueError("Некорректный формат файла JSON.")

            entry_id = str(len(data) + 1)
            data[entry_id] = entry_data

            file.seek(0)
            json.dump(data, file, indent=4, ensure_ascii=False)
            
    # 3. Редактирование записи: Изменение существующей записи.
    def edit_entry(self, entry_id: str, **kwargs: Dict[str, str]) -> None:

        with open(self.file_path, 'r+') as file:
            try:
                data: Dict[str, Dict[str, str]] = json.load(file)
            except json.JSONDecodeError:
                raise ValueError("Некорректный формат файла JSON.")
            
            if entry_id not in data:
                raise ValueError(f"Запись с ID {entry_id} не найдена.")
    
            entry: Dict[str, str] = data[entry_id]

            for key, value in kwargs.items():
                if key in entry:
                    entry[key] = value
                else:
                    raise ValueError(f"Поле '{key}' не найдено в записи.")
            
            file.seek(0)
            file.truncate()

            json.dump(data, file, indent=4, ensure_ascii=False)
    
    # 4. Поиск по записям: Поиск записей по категории, дате, сумме или описанию.
    # Поиск доступен как по одному полю, так и по нескольким полям (проверяется совпадение сразу нескольких полей)
    def search_entry(self, **kwargs: Dict[str, str]) -> Dict[str, Dict[str, str]]:
        
        with open(self.file_path, 'r') as file:
            try:
                data: Dict[str, Dict[str, str]] = json.load(file)
            except json.JSONDecodeError:
                raise ValueError("Некорректный формат файла JSON.")

            results: Dict[str, Dict[str, str]] = {}

            for entry_id, entry in data.items():
                match_all_criteria = True
                for key, value in kwargs.items():
                    if key in entry and value == entry[key]:
                        continue
                    else:
                        match_all_criteria = False
                        break
                if match_all_criteria:
                    results[entry_id] = entry

            return results
            
    # Функция для получения кортежа с тремя элементами: общий баланс, сумма доходов, сумма расходов.
    # Применяется для метода show_balance
    def get_balance(self) -> Tuple[float, float, float]:

        total_income: float = 0
        total_expense: float = 0

        with open(self.file_path, 'r') as file:
            try:
                data: Dict[str, Dict[str, str]] = json.load(file)
            except json.JSONDecodeError:
                raise ValueError("Некорректный формат файла JSON.")
            
            for entry in data.values():
                if entry["Категория"] == "Доход":
                    total_income += float(entry["Сумма"])
                elif entry["Категория"] == "Расход":
                    total_expense += float(entry["Сумма"])
        
        total_balance: float = total_income - total_expense
        return total_balance, total_income, total_expense
    
    
def main():

    file_path = 'data.json'
    wallet = Wallet(file_path)

    while True:

        print("\n")
        print("1. Показать баланс")
        print("2. Добавить запись")
        print("3. Редактировать запись")
        print("4. Поиск записей")
        print("5. Выйти")
        print("\n")

        choice = input("Выберите действие: ")

        if choice == "1":
            wallet.show_balance()
            
        elif choice == "2":
            wallet.add_entry(get_entry_data_for_add_entry())

        elif choice == "3":
            entry_id, kwargs = get_id_and_kwargs_for_edit_entry()
            wallet.edit_entry(entry_id, **kwargs)

        elif choice == "4":
            kwargs = get_kwargs_for_search_entry()
            print_results(wallet.search_entry(**kwargs))
            
        elif choice == "5":
            break

        else:
            print("Неверный выбор. Пожалуйста, выберите действие из списка.")


if __name__ == "__main__":
    main()

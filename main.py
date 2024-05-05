import json
from typing import Dict, List, Tuple

class Wallet:

    def __init__(self, file_path):
        self.file_path = file_path

    # 1. Вывод баланса: Показать текущий баланс, а также отдельно доходы и расходы.
    def show_balance(self) -> None:

        total_balance, total_income, total_expense = self.get_balance()
        print(f"Общий баланс: {total_balance}")
        print(f"Сумма доходов: {total_income}")
        print(f"Сумма расходов: {total_expense}")

    # 2. Добавление записи: Возможность добавления новой записи о доходе или расходе.
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
            
    # 3. Редактирование записи: Изменение существующих записей о доходах и расходах.
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
    
    # 4. Поиск по записям: Поиск записей по категории, дате или сумме.
    # Поиск доступен как по значению одного поля, так и по нескольким полям (проверяется совпадение сразу нескольких полей)
    def search_entry(self, **kwargs: Dict[str, str]) -> None:
        
        with open(self.file_path, 'r') as file:
            try:
                data: Dict[str, Dict[str, str]] = json.load(file)
            except json.JSONDecodeError:
                raise ValueError("Некорректный формат файла JSON.")

            results = {}

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
            
    # Вывод словаря записей. 
    # Применяется для вывода результатов search_entry
    def print_results(self, results: Dict[str, Dict[str, str]]) -> None:
        for entry_id, entry_data in results.items():
            print(f"{entry_id}: ")
            for key, value in entry_data.items():
                print(f"    {key}: {value}")
            print(" ")

    # Функция для получения кортежа с тремя элементами: общий баланс, сумма доходов, сумма расходов.
    # Применяется для show_balance
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

    # Функция для получения словаря с данными добавляемой записи.
    # Применяется для add_entry
    def get_entry_data(self) -> Dict[str, str]:
        
        date = input("Введите дату: ")
        category = str(input("Введите категорию (Доход/Расход): "))
        summ = str(float(input("Введите сумму: ")))
        description = input("Введите описание: ")
    
        if category not in ("Доход", "Расход"):
            raise ValueError("Некорректная категория. Введите 'Доход' или 'Расход'.")

        entry_data: Dict[str, str] = {
            "Дата": date,
            "Категория": category,
            "Сумма": summ,
            "Описание": description
        }
    
        return entry_data

    # Вспомогательная функция для получния id записи, которую нужно отредактировать, а также 
    # пар ключ-значение, представляющих поля и новые значения для редактирования.
    # Применяется для edit_entry
    def get_id_and_kwargs_for_edit_entry(self) -> Tuple[str, Dict[str, str]]:
        
        entry_id: str = input("Введите ID записи, которую хотите отредактировать: ")
        fields_to_edit: List[str] = input("Введите поля для редактирования через пробел: ").strip().split(' ')
        new_values: Dict[str, str] = {}

        for field in fields_to_edit:
            new_value: str = input(f"Введите новое значение для поля '{field}': ")
            if field == "Сумма":
                try:
                    new_value = str(float(new_value))
                except ValueError as e:
                    raise ValueError("Ошибка: Введите корректное числовое значение для поля 'Сумма'.") from e
            new_values[field] = new_value

        return entry_id, new_values
    
    # Вспомогательная функция для получния пар ключ-значение, представляющих поля и их значения для поиска записей.
    # Применяется для search_entry
    def get_kwargs_for_search_entry(self) -> Dict[str, str]:
    
        keys_for_search: List[str] = input("Введите поля для поиска через пробел: ").strip().split(' ')
        kwargs: Dict[str, str] = {}

        for key in keys_for_search:
            value_for_key_for_search: str = input(f"Введите значение для поля {key} поиска: ")
            if key == "Сумма":
                try:
                    value_for_key_for_search = str(float(value_for_key_for_search))
                except ValueError as e:
                    raise ValueError("Ошибка: Введите корректное числовое значение для поля 'Сумма'.") from e
            kwargs[key] = value_for_key_for_search
            
        return kwargs
    

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
            wallet.add_entry(wallet.get_entry_data())

        elif choice == "3":
            entry_id, kwargs = wallet.get_id_and_kwargs_for_edit_entry()
            wallet.edit_entry(entry_id, **kwargs)

        elif choice == "4":
            kwargs = wallet.get_kwargs_for_search_entry()
            wallet.print_results(wallet.search_entry(**kwargs))
            
        elif choice == "5":
            break

        else:
            print("Неверный выбор. Пожалуйста, выберите действие из списка.")


if __name__ == "__main__":
    main()

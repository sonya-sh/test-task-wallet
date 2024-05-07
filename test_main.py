import os
import json
import pytest
from main import (
    Wallet,
    get_date_input,
    get_category_input,
    get_entry_data_for_add_entry,
    get_id_and_kwargs_for_edit_entry,
    get_kwargs_for_search_entry,
    get_summ_input
)

@pytest.fixture(scope='class')
def test_data_file():

    data = {
        "1": {"Дата": "01-01-2024", "Категория": "Доход", "Сумма": "100.0", "Описание": "Зарплата"},
        "2": {"Дата": "02-01-2024", "Категория": "Расход", "Сумма": "20.0", "Описание": "Покупки"},
        "3": {"Дата": "02-01-2024", "Категория": "Расход", "Сумма": "10.0", "Описание": "Ещё покупки"}
    }
    with open('test_data.json', 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    yield 'test_data.json'
    
    os.remove('test_data.json')

@pytest.fixture(scope='class')
def wallet(test_data_file):
    return Wallet(test_data_file)


class TestInputFunctions:

    def test_valid_date_input(self, monkeypatch):
        input_values = ['01-01-2023']
        monkeypatch.setattr('builtins.input', lambda _: input_values.pop(0))
        assert get_date_input() == '01-01-2023'

    def test_invalid_date_input(self, monkeypatch, capsys):
        input_values = ['invalid_date', '01/01/2023', '32-01-2023', '01-13-2023', '01-01-2023']
        monkeypatch.setattr('builtins.input', lambda _: input_values.pop(0))
        result = get_date_input()
        out_str_error = capsys.readouterr()
        assert "Дата должна быть в формате дд-мм-гггг" in out_str_error.out
        assert result == '01-01-2023'

    def test_empty_date_input(self, monkeypatch, capsys):
        input_values = ['', '01-01-2023']
        monkeypatch.setattr('builtins.input', lambda _: input_values.pop(0))
        result = get_date_input()
        out_str_error = capsys.readouterr()
        assert "Дата не может быть пустой." in out_str_error.out
        assert result == '01-01-2023'

    def test_valid_category_input(self, monkeypatch):
        input_values = ['Доход']
        monkeypatch.setattr('builtins.input', lambda _: input_values.pop(0))
        assert get_category_input() == 'Доход'

    def test_invalid_category_input(self, monkeypatch, capsys):
        input_values = ['invalid_category', 'доход', 'Доход']
        monkeypatch.setattr('builtins.input', lambda _: input_values.pop(0))
        result = get_category_input()
        out_str_error = capsys.readouterr()
        assert "Некорректная категория. Введите 'Доход' или 'Расход'." in out_str_error.out
        assert result == 'Доход'

    def test_valid_sum_input(self, monkeypatch):
        input_values = ['80.7']
        monkeypatch.setattr('builtins.input', lambda _: input_values.pop(0))
        assert get_summ_input() == '80.7'

    def test_invalid_sum_input(self, monkeypatch, capsys):
        input_values = ['abc', '-abc', '80.7']
        monkeypatch.setattr('builtins.input', lambda _: input_values.pop(0))
        result = get_summ_input()
        out_str_error = capsys.readouterr()
        assert "Значение должно быть числом" in out_str_error.out
        assert result == '80.7'

    def test_negative_sum_input(self, monkeypatch, capsys):
        input_values = ['-1', '80.7']
        monkeypatch.setattr('builtins.input', lambda _: input_values.pop(0))
        result = get_summ_input()
        out_str_error = capsys.readouterr()
        assert "Значение не может быть отрицательным." in out_str_error.out
        assert result == '80.7'

@pytest.mark.usefixtures("wallet")
class TestGetBalance:

    def test_get_balance(self, wallet):
        total_balance, total_income, total_expense = wallet.get_balance()
        assert total_balance == 70.0
        assert total_income == 100.0
        assert total_expense == 30.0

@pytest.mark.usefixtures("wallet")
class TestAddEntry:

    def test_add_valid_entry(self, wallet):

        with open('test_data.json', 'r') as file:
            data_before = json.load(file)
            count_before = len(data_before)
        
            entry_data = {
                "Дата": "12-05-2024",
                "Категория": "Доход",
                "Сумма": "100.0",
                "Описание": "Зарплата"
            }
            wallet.add_entry(entry_data)
        
        with open('test_data.json', 'r') as file:
            data_after = json.load(file)
            count_after = len(data_after)

        assert count_after == count_before + 1
        assert data_after[str(count_after)] == entry_data

@pytest.mark.usefixtures("wallet")
class TestEditEntry:

    def test_edit_existing_entry(self, wallet):
        
        entry_id = "1"
        new_data = {
            "Дата": "03-01-2024",
            "Категория": "Доход",
            "Сумма": "150.0",
            "Описание": "Бонус"
        }

        wallet.edit_entry(entry_id, **new_data)

        with open(wallet.file_path, 'r') as file:
            data = json.load(file)
            assert data[entry_id] == new_data

    def test_edit_non_existing_entry(self, wallet):

        entry_id = "10"  # Несуществующий ID записи
        new_data = {
            "Дата": "04-01-2024",
        }

        with pytest.raises(ValueError):
            wallet.edit_entry(entry_id, **new_data)


    def test_edit_entry_invalid_field(self, wallet):
        
        entry_id = "1"
        new_data = {
            "Поле": "04-01-2024", # Несуществующее поле
        }  

        with pytest.raises(ValueError):
            wallet.edit_entry(entry_id, **new_data)

@pytest.mark.usefixtures("wallet")
class TestSearchEntry:

    def test_search_entry(self, wallet):

        kwargs = {'Категория':'Расход'}
        results = wallet.search_entry(**kwargs)
        assert len(results) == 2
        assert "2" in results
        assert "3" in results
        assert results["2"]["Дата"] == "02-01-2024"
        assert results["2"]["Сумма"] == "20.0"
        assert results["3"]["Дата"] == "02-01-2024"
        assert results["3"]["Сумма"] == "10.0"

    def test_search_entry_many_fields(self, wallet):

        kwargs = {'Категория':'Расход', 'Дата':'02-01-2024'}
        results = wallet.search_entry(**kwargs)
        assert len(results) == 2
        assert "2" in results
        assert "3" in results
        assert results["2"]["Дата"] == "02-01-2024"
        assert results["2"]["Сумма"] == "20.0"
        assert results["3"]["Дата"] == "02-01-2024"
        assert results["3"]["Сумма"] == "10.0"

    def test_search_entry_not_found(self, wallet):

        results = wallet.search_entry(Категория="Неизвестная категория")
        assert len(results) == 0

class TestGetEntryDataForAddEntry:

    def test_get_valid_entry_data(self, monkeypatch):

        input_values = ['05-12-2024', 'Доход', '100', 'Зарплата']
        monkeypatch.setattr('builtins.input', lambda _: input_values.pop(0))
        
        entry_data = get_entry_data_for_add_entry()

        assert entry_data == {
            "Дата": "05-12-2024",
            "Категория": "Доход",
            "Сумма": "100.0",
            "Описание": "Зарплата"
        }

class TestGetIdAndKwargsForEditEntry:

    def test_valid_input(self, monkeypatch):

        input_values = ['1', ' Дата Сумма ', '05-12-2024', '150']
        monkeypatch.setattr('builtins.input', lambda _: input_values.pop(0))

        entry_id, kwargs = get_id_and_kwargs_for_edit_entry()

        assert entry_id == '1'
        assert kwargs == {'Дата': '05-12-2024', 'Сумма': '150.0'}

class TestGetKwargsForSearchEntry:

    def test_valid_input(self, monkeypatch):

        input_values = ['Дата ', '02-01-2024']
        monkeypatch.setattr('builtins.input', lambda _: input_values.pop(0))

        kwargs = get_kwargs_for_search_entry()

        assert kwargs == {'Дата': '02-01-2024'}

    def test_valid_input_many(self, monkeypatch):

        input_values = [' Дата Категория', '02-01-2024', 'Расход']
        monkeypatch.setattr('builtins.input', lambda _: input_values.pop(0))

        kwargs = get_kwargs_for_search_entry()

        assert kwargs == {'Дата': '02-01-2024', 'Категория':'Расход'}

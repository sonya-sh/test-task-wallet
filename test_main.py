import os
import json
import pytest
from main import Wallet

@pytest.fixture(scope='module')
def test_data_file():

    data = {
        "1": {"Дата": "01.01.2024", "Категория": "Доход", "Сумма": "100.0", "Описание": "Зарплата"},
        "2": {"Дата": "02.01.2024", "Категория": "Расход", "Сумма": "20.0", "Описание": "Покупки"},
        "3": {"Дата": "02.01.2024", "Категория": "Расход", "Сумма": "10.0", "Описание": "Ещё покупки"}
    }
    with open('test_data.json', 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    yield 'test_data.json'
    
    os.remove('test_data.json')

@pytest.fixture(scope='module')
def wallet(test_data_file):
    return Wallet(test_data_file)

class TestGetBalance:

    def test_get_balance(self, wallet):
        total_balance, total_income, total_expense = wallet.get_balance()
        assert total_balance == 70.0
        assert total_income == 100.0
        assert total_expense == 30.0


class TestGetEntryData:

    def test_get_entry_data(self, monkeypatch, wallet):

        input_values = ['2024-05-12', 'Доход', '100', 'Зарплата']
        monkeypatch.setattr('builtins.input', lambda _: input_values.pop(0))
        
        entry_data = wallet.get_entry_data()

        assert entry_data == {
            "Дата": "2024-05-12",
            "Категория": "Доход",
            "Сумма": "100.0",
            "Описание": "Зарплата"
        }

    def test_get_entry_data_invalid_category(self, monkeypatch, wallet):
        
        input_values = ['2024-05-12', 'Что-то кроме Доход/Расход', '100', 'Зарплата']
        monkeypatch.setattr('builtins.input', lambda _: input_values.pop(0))
        
        with pytest.raises(ValueError):
            wallet.get_entry_data()
        
    def test_get_entry_data_invalid_summ(self, monkeypatch, wallet):
        
        input_values = ['2024-05-12', 'Расход', 'abc', 'Зарплата']
        monkeypatch.setattr('builtins.input', lambda _: input_values.pop(0))
        
        with pytest.raises(ValueError):
            wallet.get_entry_data()


class TestAddEntry:

    def test_add_valid_entry(self, wallet):

        with open('test_data.json', 'r') as file:
            data_before = json.load(file)
            count_before = len(data_before)
        
            entry_data = {
                "Дата": "2024-05-12",
                "Категория": "Доход",
                "Сумма": "100.0",
                "Описание": "Зарплата"
            }
            wallet.add_entry(entry_data)
        
        with open('test_data.json', 'r') as file:
            data_after = json.load(file)
            count_after = len(data_after)
        new_entry_id = str(count_before + 1)
        assert count_after == count_before + 1
        assert data_after[str(count_after)] == entry_data
        #assert new_entry_id == '4'


class TestGetIdAndKwargsForEditEntry:

    def test_valid_input(self, wallet, monkeypatch):

        input_values = ['1', 'Дата Сумма ', '2024-05-12', '150']
        monkeypatch.setattr('builtins.input', lambda _: input_values.pop(0))

        entry_id, kwargs = wallet.get_id_and_kwargs_for_edit_entry()

        assert entry_id == '1'
        assert kwargs == {'Дата': '2024-05-12', 'Сумма': '150.0'}

    def test_invalid_sum_input(self, wallet, monkeypatch):

        input_values = ['1', 'Дата Сумма', '2024-05-12', 'abc']
        monkeypatch.setattr('builtins.input', lambda _: input_values.pop(0))

        with pytest.raises(ValueError):
            entry_id, kwargs = wallet.get_id_and_kwargs_for_edit_entry()


class TestEditEntry:

    def test_edit_existing_entry(self, wallet):
        
        entry_id = "1"
        new_data = {
            "Дата": "03.01.2024",
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
            "Дата": "04.01.2024",
        }

        with pytest.raises(ValueError):
            wallet.edit_entry(entry_id, **new_data)


    def test_edit_entry_invalid_field(self, wallet):
        
        entry_id = "1"
        new_data = {
            "Поле": "04.01.2024", # Несуществующее поле
        }  

        with pytest.raises(ValueError):
            wallet.edit_entry(entry_id, **new_data)


class TestGetKwargsForSearchEntry:

    def test_valid_input(self, wallet, monkeypatch):

        input_values = ['Дата ', '02.01.2024']
        monkeypatch.setattr('builtins.input', lambda _: input_values.pop(0))

        kwargs = wallet.get_kwargs_for_search_entry()

        assert kwargs == {'Дата': '02.01.2024'}

    def test_valid_input_many(self, wallet, monkeypatch):

        input_values = ['Дата Категория', '02.01.2024', 'Расход']
        monkeypatch.setattr('builtins.input', lambda _: input_values.pop(0))

        kwargs = wallet.get_kwargs_for_search_entry()

        assert kwargs == {'Дата': '02.01.2024', 'Категория':'Расход'}

    def test_invalid_sum_input(self, wallet, monkeypatch):

        input_values = ['Сумма', 'abc']
        monkeypatch.setattr('builtins.input', lambda _: input_values.pop(0))

        with pytest.raises(ValueError):
            kwargs = wallet.get_kwargs_for_search_entry()

class TestSearchEntry:

    def test_search_entry(self, wallet):

        kwargs = {'Категория':'Расход'}
        results = wallet.search_entry(**kwargs)
        assert len(results) == 2
        assert "2" in results
        assert "3" in results
        assert results["2"]["Дата"] == "02.01.2024"
        assert results["2"]["Сумма"] == "20.0"
        assert results["3"]["Дата"] == "02.01.2024"
        assert results["3"]["Сумма"] == "10.0"

    def test_search_entry_many_fields(self, wallet):

        kwargs = {'Категория':'Расход', 'Дата':'02.01.2024'}
        results = wallet.search_entry(**kwargs)
        assert len(results) == 2
        assert "2" in results
        assert "3" in results
        assert results["2"]["Дата"] == "02.01.2024"
        assert results["2"]["Сумма"] == "20.0"
        assert results["3"]["Дата"] == "02.01.2024"
        assert results["3"]["Сумма"] == "10.0"

    def test_search_entry_not_found(self, wallet):

        results = wallet.search_entry(Категория="Неизвестная категория")
        assert len(results) == 0

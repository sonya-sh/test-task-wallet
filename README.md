### test-task-wallet

Тестовое задание: Консольное приложение для учета личных доходов и расходов.

Функциональность:
1. Вывод баланса: Показать текущий баланс, а также отдельно доходы и расходы.  
2. Добавление записи: Возможность добавления новой записи о доходе или расходе.  
3. Редактирование записи: Изменение существующих записей о доходах и расходах.  
4. Поиск по записям: Поиск записей по категории, дате, сумме или описанию. Возможен поиск как по одному полю, так и по нескольким.  

Как использовать:

$ git clone https://github.com/sonya-sh/test-task-wallet.git  
$ cd test-task-wallet  
$ pip install -r requirements.txt  
$ python3 main.py  
  
Выберите действие из предложенного списка:  
"1" для просмотра баланса.  
"2" для добавления новой записи.  
"3" для редактирования существующей записи.  
"4" для поиска записей.  
"5" для выхода из программы.  

Программа использует файл данных в формате JSON для хранения информации о доходах и расходах. Пользователь может изменить путь к этому файлу, указав его в переменной file_path при создании экземпляра класса Wallet.  

Пример корректного формата файла (начало обязательно с первой строки):  

```json
{
    "1": {
        "Дата": "3-05-2024",
        "Категория": "Доход",
        "Сумма": "600.0",
        "Описание": "Описание записи1"
    },
    "2": {
        "Дата": "3-04-2024",
        "Категория": "Расход",
        "Сумма": "100.0",
        "Описание": "Описание записи2"
    }
}
```

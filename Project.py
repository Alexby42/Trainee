import os
import csv
import re
from typing import List
from tabulate import tabulate


def show_result(result: List[List], headers: List[str]) -> None:
    '''Представление результата поиска в табличном формате для вывода в консоль'''

    number_result = [[i + 1] + result for i, result in enumerate(result)]
    print(tabulate(number_result, headers=headers, tablefmt='fancy_grid'))


def export_to_html(result: List[List], headers: List[str], filename: str) -> None:
    '''Экспорт результатов поиска в HTML-файл'''

    number_result = [[i + 1] + result for i, result in enumerate(result)]
    table = tabulate(number_result, headers=headers, tablefmt='html')
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(table)


class PriceMachine:
    '''Класс для загрузки, поиска и сохранения полученных данных'''
    HEADERS = ['№', 'Файл'.center(25), 'Наименование'.center(35), 'Цена'.ljust(6), 'Вес'.ljust(5), 'Цена за кг.']

    def __init__(self):
        '''Инициализация класса'''
        self.data = []

    def load_data(self, file_path: str) -> None:
        '''Загрузка данных из CSV-файла'''
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.row_handle(file_path, row)
        except (IOError, csv.Error) as e:
            print(f'Ошибка чтения файла {file_path}: {e}')

    def load_prices(self, directory: str) -> None:
        '''Загрузка цен из указанной директории'''

        self.data = []
        for filename in os.listdir(directory):
            if filename.endswith('.csv') and 'price' in filename.lower():
                self.load_data(os.path.join(filename))

    def row_handle(self, file_name: str, row: dict) -> None:
        '''Обработка строк из CSV-файла и добавление ее в список данных'''

        try:
            product_name = self.extract_value(row, r'(название|продукт|товар|наименование)')
            price = float(self.extract_value(row, r'(цена|розница)').replace(',', '.'))
            weight = float(self.extract_value(row, r'(фасовка|масса|вес)').replace(',', '.'))
            self.data.append([file_name, product_name, price, weight, round(price / weight, 2)])
        except (TypeError, ValueError) as e:
            print(f'Ошибка при обработке строки {row}: {e}')

    def extract_value(self, row: dict, pattern: str) -> str:
        '''Извлекает значение из строки на основе регулярного выражения'''

        for column_name, value in row.items():
            if re.search(pattern, column_name, re.IGNORECASE):
                return value.strip()
        return ''

    def search_element(self, query: str) -> List[List]:
        '''Поиск элементов на основе запроса'''

        result = [row for row in self.data if re.search(query, row[1], re.IGNORECASE)]
        return sorted(result, key=lambda x: x[4])

    def export_to_html_all(self, fname='output_all.html'):
        '''Экспорт полного списка всех прайсов в HTML-файл с предварительной сортировкой по цене за кг.'''

        self.data.sort(key=lambda row: row[4])
        res = '''
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="UTF-8">
            <title>Список товара</title>
        </head>
        <body>
            <table width="70%" border="3px" bgcolor="#89EC6A" align="center">
                <tr>
                    <th>Номер</th>
                    <th>Файл</th>
                    <th>Наименование</th>
                    <th>Цена</th>
                    <th>Вес</th>
                    <th>Цена за кг.</th>
                </tr>
        '''
        count_ = 1
        for line in self.data:
            res += f'<tr>'
            res += f'<td>{count_}</td>'
            res += f'<td>{line[0]}</td>'
            res += f'<td>{line[1]}</td>'
            res += f'<td>{line[2]}</td>'
            res += f'<td>{line[3]}</td>'
            res += f'<td>{line[4]}</td>'
            res += f'</tr>'
            count_ += 1
        res += '''
        </table>
        </body>
        </html>
        '''
        with open(fname, 'w', encoding='utf8') as f:
            f.write(res)
        print(f'Общие данные всего ассортимента сохранены в файл {fname}')

    def find_text(self, query: str) -> None:
        '''Поиск и отображение текста'''
        result = self.search_element(query)
        show_result(result, self.HEADERS)
        html_filename = 'output_find.html'
        export_to_html(result, self.HEADERS, html_filename)
        print(f'Результаты поиска сохранены в файл: {html_filename}')
        self.export_to_html_all()

    def main(self, directory: str) -> None:
        '''Главный метод для работы с классом PriceMachine'''

        self.load_prices(directory)
        while True:
            query = input("Введите запрос ('exit' - выход): ")
            if query.lower() in 'exit':
                print('Работа завершена!')
                break
            self.find_text(query)


if __name__ == "__main__":
    pm = PriceMachine()
    current_directory = os.path.dirname(os.path.abspath(__file__))
    pm.main(current_directory)

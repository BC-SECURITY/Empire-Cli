from typing import List

from terminaltables import SingleTable


def print_table(data: List[List[str]] = None, title: str = ''):
    if data is None:
        return

    table = SingleTable(data)
    table.title = title
    table.inner_row_border = True

    print(table.table)

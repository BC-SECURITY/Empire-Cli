from datetime import datetime
from typing import List

from terminaltables import SingleTable

import src.utils.print_util as print_utils


def print_table(data: List[List[str]] = None, title: str = ''):
    if data is None:
        return

    # Make header blue
    for x in range(len(data[0])):
        data[0][x] = print_utils.color(data[0][x], 'blue')

    table = SingleTable(data)
    table.title = title
    table.inner_row_border = True

    print(table.table)


def print_agent_table(data: List[List[str]] = None, formatting: List[List[str]] = None, title: str = ''):
    if data is None:
        return

    # Make header blue
    for x in range(len(data[0])):
        data[0][x] = print_utils.color(data[0][x], 'blue')

    for x in range(len(data))[1:]:
        # Add asterisk for high-integrity agents
        if formatting[x][1]:
            data[x][1] = data[x][1] + '*'

        # color agents
        if formatting[x][0]:
            color = 'red'
        elif not formatting[x][0]:
            color = 'green'

        # Set colors for entire row
        for y in range(len(data[x])):
            data[x][y] = print_utils.color(data[x][y], color)

    table = SingleTable(data)
    table.title = title
    table.inner_row_border = True

    print(table.table)

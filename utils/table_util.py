from datetime import datetime, timezone
from typing import List

from terminaltables import SingleTable
import utils.print_util as print_utils


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


def print_agent_table(data: List[List[str]] = None, title: str = ''):
    if data is None:
        return

    # Make header blue
    for x in range(len(data[0])):
        data[0][x] = print_utils.color(data[0][x], 'blue')

    for x in range(len(data))[1:]:
        stamp_date = datetime.strptime(data[x][9], "%Y-%m-%dT%H:%M:%S.%f%z").astimezone(tz=None)  # Display local
        stamp_display_local = stamp_date.strftime('%Y-%m-%d %H:%M:%S')

        # Get values for color
        delta = getutcnow() - stamp_date
        delay = data[x][8].split("/")[0]
        jitter = data[x][8].split("/")[1].split(".")[1]

        # color agents
        if delta.total_seconds() > int(delay) * (int(jitter) + 1) * 7:
            data[x][9] = stamp_display_local
            color = 'red'
        elif delta.total_seconds() > int(delay) * (int(jitter) + 1) * 3:
            data[x][9] = stamp_display_local
            color = 'yellow'
        else:
            data[x][9] = stamp_display_local
            color = 'green'

        # Set colors for entire row
        for y in range(len(data[x])):
            data[x][y] = print_utils.color(data[x][y], color)

    table = SingleTable(data)
    table.title = title
    table.inner_row_border = True

    print(table.table)


def getutcnow():
    return datetime.now(timezone.utc)

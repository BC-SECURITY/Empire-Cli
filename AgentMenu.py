import shlex
import string
import textwrap

from prompt_toolkit.completion import Completion
from terminaltables import SingleTable

from EmpireCliState import state
from utils import register_cli_commands, command

# This needs to be updated to match how ListenerMenu works.
class AgentMenu(object):
    def __init__(self):
        self.display_name = "agents"

    def autocomplete(self):
        return [
            'list',
        ]

    def execute(self, text: string) -> None:
        if text == 'list':
            agents = state.get_agents()
            agent_list = list(map(lambda x: [x['name'], x['listener'], x['language'], x['username'], trunc(x['process_name'], 10), x['process_id'], x['lastseen_time']], agents['agents']))
            agent_list.insert(0, ['Name', 'Listener', 'Language', 'Username', 'Process', 'PID', 'Last Seen'])
            table = SingleTable(agent_list)
            table.title = 'Agents List'
            table.inner_row_border = True
            print(table.table)
        # print('hi!' + text)

    @command
    def list(self) -> None:
        """
        Get running/available listeners

        Usage: list
        """
        agent_list = list(map(lambda x: [x['ID'], x['session_id'], x['high_integrity'], x['language'], x['internal_ip'], x['username'], x['process_name'], x['process_id'], str(x['delay']) + '/' + str(x['jitter']), x['lastseen_time'], x['listener']],
                                 state.get_agents()['agents']))
        agent_list.insert(0, ['ID', 'Session ID', 'High Integrity', 'Language', 'Internal IP', 'Username', 'Process', 'PID', 'Delay', 'Last Seen', 'Listener'])
        table = SingleTable(agent_list)
        table.title = 'Agents'
        table.inner_row_border = True
        print(table.table)


def trunc(value: string = '', limit: int = 1) -> string:
    if value:
        if len(value) > limit:
            return value[:limit - 2] + '..'
        else:
            return value
    return ''

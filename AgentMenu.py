import shlex
import string
import textwrap

from prompt_toolkit.completion import Completion
from terminaltables import SingleTable

from EmpireCliState import state
from utils import register_cli_commands, command

@register_cli_commands
class AgentMenu(object):
    def __init__(self):
        self.display_name = "agents"
        self.selected_type = ''

    def autocomplete(self):
        return self._cmd_registry + [
            'help',
            'main',
            'list',
            'interact',
        ]

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()
        try:
            cmd_line = list(map(lambda s: s.lower(), shlex.split(document.current_line)))
            # print(cmd_line)
        except ValueError:
            pass
        else:
            if len(cmd_line) > 0 and cmd_line[0] in ['interact']:
                for x in range(len(state.get_agents()['agents'])):
                    #if state.get_agents()['agents'][x]['Name'] == self.selected_type:
                    type = state.get_agents()['agents'][x]['name']
                    yield Completion(type, start_position=-len(word_before_cursor))
            else:
                for word in self.autocomplete():
                    if word.startswith(word_before_cursor):
                        yield Completion(word, start_position=-len(word_before_cursor), style="underline")

    @command
    def list(self) -> None:
        """
        Get running/available agents

        Usage: list
        """
        agent_list = list(map(lambda x: [x['ID'], x['session_id'], x['high_integrity'], x['language'], x['internal_ip'], x['username'], x['process_name'], x['process_id'], str(x['delay']) + '/' + str(x['jitter']), x['lastseen_time'], x['listener']],
                                 state.get_agents()['agents']))
        agent_list.insert(0, ['ID', 'Session ID', 'High Integrity', 'Language', 'Internal IP', 'Username', 'Process', 'PID', 'Delay', 'Last Seen', 'Listener'])
        table = SingleTable(agent_list)
        table.title = 'Agents'
        table.inner_row_border = True
        print(table.table)

    @command
    def interact(self, session: string):
        """
        Interact with an active agent

        Usage: interact <session>
        """
        self.selected_type = session
        self.display_name = session

def trunc(value: string = '', limit: int = 1) -> string:
    if value:
        if len(value) > limit:
            return value[:limit - 2] + '..'
        else:
            return value
    return ''

import shlex
import string

from prompt_toolkit.completion import Completion
from terminaltables import SingleTable

from EmpireCliState import state
from Menu import Menu
from utils import register_cli_commands, command


@register_cli_commands
class AgentMenu(Menu):
    def __init__(self):
        super().__init__(display_name='agents', selected='')

    def autocomplete(self):
        return self._cmd_registry + super().autocomplete()

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()
        try:
            cmd_line = list(map(lambda s: s.lower(), shlex.split(document.current_line)))
            # print(cmd_line)
        except ValueError:
            pass
        else:
            if len(cmd_line) > 0 and cmd_line[0] in ['kill', 'info', 'clear', 'rename']:
                for type in state.agent_types:
                    yield Completion(type, start_position=-len(word_before_cursor))
            else:
                yield from super().get_completions(document, complete_event)

    def init(self):
        self.list()

    @command
    def list(self) -> None:
        """
        Get running/available agents

        Usage: list
        """
        agent_list = list(map(
            lambda x: [x['ID'], x['name'], x['high_integrity'], x['language'], x['internal_ip'], x['username'],
                       x['process_name'], x['process_id'], str(x['delay']) + '/' + str(x['jitter']), x['lastseen_time'],
                       x['listener']],
            state.get_agents()['agents']))
        agent_list.insert(0, ['ID', 'name', 'High Integrity', 'Language', 'Internal IP', 'Username', 'Process',
                              'PID', 'Delay', 'Last Seen', 'Listener'])
        table = SingleTable(agent_list)
        table.title = 'Agents'
        table.inner_row_border = True
        print(table.table)

    @command
    def kill(self, agent_name: string) -> None:
        """
        Kill the selected listener

        Usage: kill <agent_name>
        """
        state.kill_agent(agent_name)

    @command
    def clear(self, agent_name: string) -> None:
        """
        Clear tasks for selected listener

        Usage: clear <agent_name>
        """
        state.clear_agent(agent_name)

    @command
    def rename(self, agent_name: string, new_agent_name: string) -> None:
        """
        Rename selected listener

        Usage: rename <agent_name> <new_agent_name>
        """
        state.rename_agent(agent_name, new_agent_name)


def trunc(value: string = '', limit: int = 1) -> string:
    if value:
        if len(value) > limit:
            return value[:limit - 2] + '..'
        else:
            return value
    return ''


agent_menu = AgentMenu()

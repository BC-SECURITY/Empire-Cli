import string

from prompt_toolkit.completion import Completion

import table_util
from EmpireCliState import state
from Menu import Menu
from utils.autocomplete_utils import filtered_search_list, position_util
from utils.cli_utils import register_cli_commands, command


@register_cli_commands
class AgentMenu(Menu):
    def __init__(self):
        super().__init__(display_name='agents', selected='')

    def autocomplete(self):
        return self._cmd_registry + super().autocomplete()

    def get_completions(self, document, complete_event, cmd_line, word_before_cursor):
        if cmd_line[0] in ['kill', 'info', 'clear', 'rename'] and position_util(cmd_line, 2, word_before_cursor):
            for agent in filtered_search_list(word_before_cursor, state.agents.keys()):
                yield Completion(agent, start_position=-len(word_before_cursor))
        elif position_util(cmd_line, 1, word_before_cursor):
            yield from super().get_completions(document, complete_event, cmd_line, word_before_cursor)

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
            state.get_agents()))
        agent_list.insert(0, ['ID', 'name', 'High Integrity', 'Language', 'Internal IP', 'Username', 'Process',
                              'PID', 'Delay', 'Last Seen', 'Listener'])

        table_util.print_table(agent_list, 'Agents')

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

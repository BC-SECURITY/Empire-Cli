import shlex
import string
import textwrap

from prompt_toolkit.completion import Completion
from terminaltables import SingleTable

from EmpireCliState import state
from utils import register_cli_commands, command


@register_cli_commands
class PluginsMenu(object):
    def __init__(self):
        self.selected_type = ''
        self.display_name = 'plugins'

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
            for word in self.autocomplete():
                if word.startswith(word_before_cursor):
                    yield Completion(word, start_position=-len(word_before_cursor), style="underline")

    @command
    def list(self) -> None:
        """
        Get active plugins

        Usage: list
        """
        plugins_list = list(map(
            lambda x: [x['Name'], x['Description']],state.list_active_plugins()['plugins']))
        plugins_list.insert(0, ['Name', 'Description'])
        table = SingleTable(plugins_list)
        table.title = 'Plugins'
        table.inner_row_border = True
        print(table.table)

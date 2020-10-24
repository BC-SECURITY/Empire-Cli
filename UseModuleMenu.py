import shlex
import string
import textwrap

from prompt_toolkit.completion import Completion
from terminaltables import SingleTable

from EmpireCliState import state
from utils import register_cli_commands, command


@register_cli_commands
class UseModuleMenu(object):
    def __init__(self):
        self.display_name = "usemodule"
        self.selected_type = ''
        self.module_options = {}

    def autocomplete(self):
        return self._cmd_registry + [
            'help',
            'main',
        ]

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()
        try:
            cmd_line = list(map(lambda s: s.lower(), shlex.split(document.current_line)))
            # print(cmd_line)
        except ValueError:
            pass
        else:
            if len(cmd_line) > 0 and cmd_line[0] in ['usemodule']:
                for type in state.module_types['types']:
                    yield Completion(type, start_position=-len(word_before_cursor))
            else:
                for word in self.autocomplete():
                    if word.startswith(word_before_cursor):
                        yield Completion(word, start_position=-len(word_before_cursor), style="underline")

    @command
    def use(self, module: str) -> None:
        """
        Use the selected module

        Usage: use <module>
        """
        if module in state.module_types['types']:
            self.selected_type = module
            self.display_name = 'usemodule/' + self.selected_type
            for x in range(len(state.modules['modules'])):
                if state.modules['modules'][x]['Name'] == self.selected_type:
                    self.module_options = state.modules['modules'][x]['options']

            module_list = []
            for key, value in self.module_options.items():
                values = list(map(lambda x: '\n'.join(textwrap.wrap(str(x), width=35)), value.values()))
                values.reverse()
                temp = [key] + values
                module_list.append(temp)

            table = SingleTable(module_list)
            table.title = 'Module Options'
            table.inner_row_border = True
            print(table.table)

    @command
    def set(self, key: string, value: string) -> None:
        """
        Set a field for the current listener

        Usage: set <key> <value>
        """
        if key in self.listener_options:
            self.module_options[key]['Value'] = value

        # todo use python prompt print methods for formatting
        print(f'Set {key} to {value}')

    @command
    def unset(self, key: str) -> None:
        """
        Unset a listener option.

        Usage: unset <key>
        """
        if key in self.listener_options:
            self.module_options[key]['Value'] = ''

        # todo use python prompt print methods for formatting
        print(f'Unset {key}')

    @command
    def info(self):
        """
        Print the current listener options

        Usage: info
        """
        module_list = []
        for key, value in self.module_options.items():
            values = list(map(lambda x: '\n'.join(textwrap.wrap(str(x), width=35)), value.values()))
            values.reverse()
            temp = [key] + values
            module_list.append(temp)

        table = SingleTable(module_list)
        table.title = 'Module Options'
        table.inner_row_border = True
        print(table.table)

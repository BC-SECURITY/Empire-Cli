import shlex
import string
import textwrap

from prompt_toolkit.completion import Completion

import table_util
from EmpireCliState import state
from Menu import Menu
from utils import register_cli_commands, command, filtered_search_list, position_util


@register_cli_commands
class UseStagerMenu(Menu):
    def __init__(self):
        super().__init__(display_name='usestager', selected='')
        self.stager_options = {}

    def autocomplete(self):
        return self._cmd_registry + super().autocomplete()

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor(WORD=True)
        try:
            # cmd_line = list(map(lambda s: s.lower(), shlex.split(document.current_line)))
            cmd_line = list(map(lambda s: s, shlex.split(document.current_line)))
            if len(cmd_line) == 0:
                cmd_line.append('')
            # print(cmd_line)
        except ValueError:
            pass
        else:
            if cmd_line[0] == 'usestager' and position_util(cmd_line, 2, word_before_cursor):
                for stager in filtered_search_list(word_before_cursor, state.stagers.keys()):
                    yield Completion(stager, start_position=-len(word_before_cursor))
            elif cmd_line[0] in ['set', 'unset'] and position_util(cmd_line, 2, word_before_cursor):
                for option in filtered_search_list(word_before_cursor, self.stager_options):
                    yield Completion(option, start_position=-len(word_before_cursor))
            elif cmd_line[0] == 'set' and position_util(cmd_line, 3, word_before_cursor):
                if len(cmd_line) > 1 and cmd_line[1] == 'Listener':
                    for listener in filtered_search_list(word_before_cursor, state.listeners.keys()):
                        yield Completion(listener, start_position=-len(word_before_cursor))
            elif position_util(cmd_line, 1, word_before_cursor):
                yield from super().get_completions(document, complete_event)

    def init(self):
        self.info()

    @command
    def use(self, module: string) -> None:
        """
        Use the selected stager.

        Usage: use <module>
        """
        if module in state.stagers.keys(): # todo rename module?
            self.selected = module
            self.display_name = 'usestager/' + module
            self.stager_options = state.stagers[module]['options']

            listener_list = []
            for key, value in self.stager_options.items():
                values = list(map(lambda x: '\n'.join(textwrap.wrap(str(x), width=35)), value.values()))
                values.reverse()
                temp = [key] + values
                listener_list.append(temp)

    @command
    def set(self, key: string, value: string) -> None:
        """
        Set a field for the current stager

        Usage: set <key> <value>
        """
        if key in self.stager_options:
            self.stager_options[key]['Value'] = value

        # todo use python prompt print methods for formatting
        print(f'Set {key} to {value}')

    @command
    def unset(self, key: str) -> None:
        """
        Unset a stager option.

        Usage: unset <key>
        """
        if key in self.stager_options:
            self.stager_options[key]['Value'] = ''

        # todo use python prompt print methods for formatting
        print(f'Unset {key}')

    @command
    def info(self):
        """
        Print the current stager options

        Usage: info
        """
        listener_list = []
        for key, value in self.stager_options.items():
            values = list(map(lambda x: '\n'.join(textwrap.wrap(str(x), width=35)), value.values()))
            values.reverse()
            temp = [key] + values
            listener_list.append(temp)

        table_util.print_table(listener_list, 'Stager Options')

    @command
    def generate(self):
        """
        Generate the stager listener

        Usage: generate
        """
        # todo validation and error handling
        # Hopefully this will force us to provide more info in api errors ;)
        post_body = {}
        for key, value in self.stager_options.items():
            post_body[key] = self.stager_options[key]['Value']

        response = state.create_stager(self.selected, post_body)

        print(response[self.selected]['Output'])


use_stager_menu = UseStagerMenu()

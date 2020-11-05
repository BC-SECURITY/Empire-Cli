import shlex
import string
import textwrap

from prompt_toolkit.completion import Completion

import print_util
import table_util
from EmpireCliState import state
from Menu import Menu
from utils import register_cli_commands, command


@register_cli_commands
class UseListenerMenu(Menu):
    def __init__(self):
        super().__init__(display_name='uselistener', selected='')
        self.listener_options = {}

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
            if len(cmd_line) > 0 and cmd_line[0] in ['uselistener']:
                for type in state.listener_types:
                    yield Completion(type, start_position=-len(word_before_cursor))
            elif len(cmd_line) > 0 and cmd_line[0] in ['set']:
                for type in state.get_listener_options(self.selected)['listeneroptions']:
                    yield Completion(type, start_position=-len(word_before_cursor))
            else:
                yield from super().get_completions(document, complete_event)

    def init(self):
        self.info()

    @command
    def use(self, module: str) -> None:
        """
        Use the selected listener

        Usage: use <module>
        """
        if module in state.listener_types:
            self.selected = module
            self.display_name = 'uselistener/' + self.selected
            self.listener_options = state.get_listener_options(self.selected)['listeneroptions']

            listener_list = []
            for key, value in self.listener_options.items():
                values = list(map(lambda x: '\n'.join(textwrap.wrap(str(x), width=35)), value.values()))
                values.reverse()
                temp = [key] + values
                listener_list.append(temp)

    @command
    def set(self, key: string, value: string) -> None:
        """
        Set a field for the current listener

        Usage: set <key> <value>
        """
        if key in self.listener_options:
            self.listener_options[key]['Value'] = value

        # todo use python prompt print methods for formatting
        print(print_util.color('[*] Set %s to %s' % (key, value)))

    @command
    def unset(self, key: str) -> None:
        """
        Unset a listener option.

        Usage: unset <key>
        """
        if key in self.listener_options:
            self.listener_options[key]['Value'] = ''

        # todo use python prompt print methods for formatting
        print(print_util.color('[*] Unset %s' % key))

    @command
    def info(self):
        """
        Print the current listener options

        Usage: info
        """
        listener_list = []
        for key, value in self.listener_options.items():
            values = list(map(lambda x: '\n'.join(textwrap.wrap(str(x), width=35)), value.values()))
            values.reverse()
            temp = [key] + values
            listener_list.append(temp)

        table_util.print_table(listener_list, 'Listeners Options')

    @command
    def start(self):
        """
        Create the current listener

        Usage: start
        """
        # todo validation and error handling
        # todo alias start to execute and generate
        # Hopefully this will force us to provide more info in api errors ;)
        post_body = {}
        for key, value in self.listener_options.items():
            post_body[key] = self.listener_options[key]['Value']

        response = state.create_listener(self.selected, post_body)
        if response['success']:
            print(print_util.color('[+] ' + response['success']))
        elif response['error']:
            print(print_util.color('[!] Error: ' + response['error']))


use_listener_menu = UseListenerMenu()

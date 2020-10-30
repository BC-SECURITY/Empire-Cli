import shlex
import string
import textwrap

from prompt_toolkit.completion import Completion
from terminaltables import SingleTable

import Helpers
from EmpireCliState import state
from utils import register_cli_commands, command


@register_cli_commands
class UsePluginMenu(object):
    def __init__(self):
        self.selected_type = ''
        self.display_name = 'useplugin'
        self.plugin_options = {}
        self.plugin_info = {}

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
            if len(cmd_line) > 0 and cmd_line[0] in ['useplugin']:
                for type in state.plugin_types['types']:
                    yield Completion(type, start_position=-len(word_before_cursor))
            else:
                for word in self.autocomplete():
                    if word.startswith(word_before_cursor):
                        yield Completion(word, start_position=-len(word_before_cursor), style="underline")

    @command
    def use(self, plugin_name: str) -> None:
        """
        Use the selected plugin

        Usage: use <plugin_name>
        """
        if plugin_name in state.plugin_types['types']:
            self.selected_type = plugin_name
            self.display_name = 'useplugin/' + self.selected_type
            for x in range(len(state.plugins['plugins'])):
                if state.plugins['plugins'][x]['Name'] == self.selected_type:
                    self.plugin_options = state.plugins['plugins'][x]['options']
                    self.plugin_info = state.plugins['plugins'][x]
                    del self.plugin_info['options']

    @command
    def info(self):
        """
        Print the plugin options

        Usage: info
        """
        plugin_list = []
        for key, value in self.plugin_options.items():
            values = list(map(lambda x: '\n'.join(textwrap.wrap(str(x), width=35)), value.values()))
            values.reverse()
            temp = [key] + values
            plugin_list.append(temp)

        table = SingleTable(plugin_list)
        table.title = 'Plugin Options'
        table.inner_row_border = True
        print(table.table)

    @command
    def set(self, key: string, value: string) -> None:
        """
        Set a field for the current plugin

        Usage: set <key> <value>
        """
        if key in self.plugin_options:
            self.plugin_options[key]['Value'] = value

        # todo use python prompt print methods for formatting
        print(Helpers.color('[*]Set {key} to {value}'))

    @command
    def unset(self, key: str) -> None:
        """
        Unset a plugin option.

        Usage: unset <key>
        """
        if key in self.plugin_options:
            self.plugin_options[key]['Value'] = ''

        # todo use python prompt print methods for formatting
        print(Helpers.color('[*] Unset {key}'))

    @command
    def execute(self):
        """
        Run current plugin

        Usage: start
        """
        # todo validation and error handling
        # Hopefully this will force us to provide more info in api errors ;)
        post_body = {}
        for key, value in self.plugin_options.items():
            post_body[key] = self.plugin_options[key]['Value']

        response = state.execute_plugin(self.selected_type, post_body)
        #print(response)

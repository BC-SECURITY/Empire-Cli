import shlex
import string
import textwrap

from prompt_toolkit.completion import Completion

import table_util
from EmpireCliState import state
from Menu import Menu
from utils import register_cli_commands, command, position_util, filtered_search_list


@register_cli_commands
class UsePluginMenu(Menu):
    def __init__(self):
        super().__init__(display_name='useplugin', selected='')
        self.plugin_options = {}
        self.plugin_info = {}

    def autocomplete(self):
        return self._cmd_registry + super().autocomplete()

    def get_completions(self, document, complete_event, cmd_line, word_before_cursor):
        if cmd_line[0] == 'useplugin' and position_util(cmd_line, 2, word_before_cursor):
            for plugin in filtered_search_list(word_before_cursor, state.plugins.keys()):
                yield Completion(plugin, start_position=-len(word_before_cursor))
        elif position_util(cmd_line, 1, word_before_cursor):
            yield from super().get_completions(document, complete_event, cmd_line, word_before_cursor)

    @command
    def use(self, plugin_name: str) -> None:
        """
        Use the selected plugin

        Usage: use <plugin_name>
        """
        if plugin_name in state.plugins:
            self.selected = plugin_name
            self.display_name = 'useplugin/' + self.selected
            self.plugin_options = state.plugins[plugin_name]['options']
            self.plugin_info = state.plugins[plugin_name]
            del self.plugin_info['options'] # todo why the del?

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

        table_util.print_table(plugin_list, 'Plugin Options')

    @command
    def set(self, key: string, value: string) -> None:
        """
        Set a field for the current plugin

        Usage: set <key> <value>
        """
        if key in self.plugin_options:
            self.plugin_options[key]['Value'] = value

        # todo use python prompt print methods for formatting
        print(f'Set {key} to {value}')

    @command
    def unset(self, key: str) -> None:
        """
        Unset a plugin option.

        Usage: unset <key>
        """
        if key in self.plugin_options:
            self.plugin_options[key]['Value'] = ''

        # todo use python prompt print methods for formatting
        print(f'Unset {key}')

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

        response = state.execute_plugin(self.selected, post_body)
        #print(response)


use_plugin_menu = UsePluginMenu()

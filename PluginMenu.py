import shlex

import table_util
from EmpireCliState import state
from Menu import Menu
from utils import register_cli_commands, command


@register_cli_commands
class PluginMenu(Menu):
    def __init__(self):
        super().__init__(display_name='plugins', selected='')

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
            yield from super().get_completions(document, complete_event)

    def init(self):
        self.list()

    @command
    def list(self) -> None:
        """
        Get active plugins

        Usage: list
        """
        plugins_list = list(map(
            lambda x: [x['Name'], x['Description']], state.get_active_plugins().values()))
        plugins_list.insert(0, ['Name', 'Description'])

        table_util.print_table(plugins_list, 'Plugins')


plugin_menu = PluginMenu()

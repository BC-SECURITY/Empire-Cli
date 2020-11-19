import string
import textwrap

from prompt_toolkit.completion import Completion

from src.utils import table_util, print_util
from src.EmpireCliState import state
from src.menus.Menu import Menu
from src.utils.autocomplete_util import filtered_search_list, position_util
from src.utils.cli_utils import register_cli_commands, command


@register_cli_commands
class UseStagerMenu(Menu):
    def __init__(self):
        super().__init__(display_name='usestager', selected='')
        self.stager_options = {}

    def autocomplete(self):
        return self._cmd_registry + super().autocomplete()

    def get_completions(self, document, complete_event, cmd_line, word_before_cursor):
        if cmd_line[0] == 'usestager' and position_util(cmd_line, 2, word_before_cursor):
            for stager in filtered_search_list(word_before_cursor, state.stagers.keys()):
                yield Completion(stager, start_position=-len(word_before_cursor))
        elif cmd_line[0] in ['set', 'unset'] and position_util(cmd_line, 2, word_before_cursor):
            for option in filtered_search_list(word_before_cursor, self.stager_options):
                yield Completion(option, start_position=-len(word_before_cursor))
        elif cmd_line[0] == 'set' and position_util(cmd_line, 3, word_before_cursor):
            if len(cmd_line) > 1 and cmd_line[1] == 'listener':
                for listener in filtered_search_list(word_before_cursor, state.listeners.keys()):
                    yield Completion(listener, start_position=-len(word_before_cursor))
        elif position_util(cmd_line, 1, word_before_cursor):
            yield from super().get_completions(document, complete_event, cmd_line, word_before_cursor)

    def init(self, **kwargs) -> bool:
        if 'selected' not in kwargs:
            return False
        else:
            self.use(kwargs['selected'])
            self.info()
            return True

    def use(self, module: string) -> None:
        """
        Use the selected stager.

        Usage: use <module>
        """
        if module in state.stagers.keys(): # todo rename module?
            self.selected = module
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
        print(print_util.color('[*] Set %s to %s' % (key, value)))

    @command
    def unset(self, key: str) -> None:
        """
        Unset a stager option.

        Usage: unset <key>
        """
        if key in self.stager_options:
            self.stager_options[key]['Value'] = ''

        # todo use python prompt print methods for formatting
        print(print_util.color('[*] Unset %s' % key))

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

        listener_list.insert(0, ['Name', 'Required', 'Value', 'Description'])

        table_util.print_table(listener_list, 'Stager Options')

    @command
    def execute(self):
        """
        Execute the stager

        Usage: execute
        """
        # todo validation and error handling
        # Hopefully this will force us to provide more info in api errors ;)
        post_body = {}
        for key, value in self.stager_options.items():
            post_body[key] = self.stager_options[key]['Value']

        response = state.create_stager(self.selected, post_body)

        print(response[self.selected]['Output'])

    @command
    def generate(self):
        """
        Generate the stager

        Usage: generate
        """
        self.execute()


use_stager_menu = UseStagerMenu()

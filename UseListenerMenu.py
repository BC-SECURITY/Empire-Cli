import string
import textwrap

from prompt_toolkit.completion import Completion

from utils import print_util, table_util
from EmpireCliState import state
from Menu import Menu
from utils.autocomplete_utils import filtered_search_list, position_util
from utils.cli_utils import register_cli_commands, command


@register_cli_commands
class UseListenerMenu(Menu):
    def __init__(self):
        super().__init__(display_name='uselistener', selected='')
        self.listener_options = {}

    def autocomplete(self):
        return self._cmd_registry + super().autocomplete()

    def get_completions(self, document, complete_event, cmd_line, word_before_cursor):
        if cmd_line[0] == 'uselistener' and position_util(cmd_line, 2, word_before_cursor):
            for listener in filtered_search_list(word_before_cursor, state.listener_types):
                yield Completion(listener, start_position=-len(word_before_cursor))
        elif cmd_line[0] in ['set', 'unset'] and position_util(cmd_line, 2, word_before_cursor):
            # Todo need to refactor to not make api requests on every autocomplete. Look at usestager
            for option in filtered_search_list(word_before_cursor, state.get_listener_options(self.selected)['listeneroptions']):
                yield Completion(option, start_position=-len(word_before_cursor))
        elif position_util(cmd_line, 1, word_before_cursor):
            yield from super().get_completions(document, complete_event, cmd_line, word_before_cursor)

    def init(self, **kwargs) -> bool:
        if 'selected' not in kwargs:
            return False
        else:
            self.use(kwargs['selected'])
            self.info()
            return True

    def use(self, module: str) -> None:
        """
        Use the selected listener

        Usage: use <module>
        """
        if module in state.listener_types:
            self.selected = module
            self.listener_options = state.get_listener_options(self.selected)['listeneroptions']

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

        listener_list.insert(0, ['Name', 'Required', 'Value', 'Description'])

        table_util.print_table(listener_list, 'Listeners Options')

    @command
    def execute(self):
        """
        Create the current listener

        Usage: execute
        """
        # todo validation and error handling
        # todo alias start to execute and generate
        # Hopefully this will force us to provide more info in api errors ;)
        post_body = {}
        for key, value in self.listener_options.items():
            post_body[key] = self.listener_options[key]['Value']

        response = state.create_listener(self.selected, post_body)
        if 'success' in response.keys():
            return
        elif 'error' in response.keys():
            print(print_util.color('[!] Error: ' + response['error']))

    @command
    def generate(self):
        """
        Create the current listener

        Usage: generate
        """
        self.execute()


use_listener_menu = UseListenerMenu()

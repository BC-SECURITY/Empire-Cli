from prompt_toolkit.completion import Completion

from src.EmpireCliState import state
from src.menus.UseMenu import UseMenu
from src.utils import print_util
from src.utils.autocomplete_util import filtered_search_list, position_util
from src.utils.cli_utils import register_cli_commands, command


@register_cli_commands
class UseListenerMenu(UseMenu):
    def __init__(self):
        super().__init__(display_name='uselistener', selected='', record_options=None)

    def autocomplete(self):
        return self._cmd_registry + super().autocomplete()

    def get_completions(self, document, complete_event, cmd_line, word_before_cursor):
        if cmd_line[0] == 'uselistener' and position_util(cmd_line, 2, word_before_cursor):
            for listener in filtered_search_list(word_before_cursor, state.listener_types):
                yield Completion(listener, start_position=-len(word_before_cursor))
        else:
            yield from super().get_completions(document, complete_event, cmd_line, word_before_cursor)

    def on_enter(self, **kwargs) -> bool:
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
            self.record_options = state.get_listener_options(self.selected)['listeneroptions']

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
        for key, value in self.record_options.items():
            post_body[key] = self.record_options[key]['Value']

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

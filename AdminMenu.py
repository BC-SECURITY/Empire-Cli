import string
import textwrap

from prompt_toolkit.completion import Completion

from utils import table_util, print_util
from EmpireCliState import state
from Menu import Menu
from utils.autocomplete_utils import filtered_search_list, position_util
from utils.cli_utils import register_cli_commands, command


@register_cli_commands
class AdminMenu(Menu):
    def __init__(self):
        super().__init__(display_name='admin', selected='')

    def autocomplete(self):
        return self._cmd_registry + super().autocomplete()

    def get_completions(self, document, complete_event, cmd_line, word_before_cursor):
        if position_util(cmd_line, 1, word_before_cursor):
            yield from super().get_completions(document, complete_event, cmd_line, word_before_cursor)

    def init(self):
        return True

    @command
    def obfuscate(self, obfucate_bool: str):
        """
        Turn on obfuscate all future powershell commands run on all agents. CANNOT BE USED WITH KEYWORD_OBFUSCATION.

        Usage: obfuscate <obfucate_bool>
        """
        # todo: should it be set <key> <value> to be consistent?
        if obfucate_bool.lower() in ['true', 'false']:
            options = {'obfuscate': obfucate_bool}
            response = state.set_admin_options(options)
        else:
            print(print_util.color('[!] Error: Invalid entry'))

        # Return results and error message
        if 'success' in response.keys():
            print(print_util.color('[*] Set obfuscate to %s' % (obfucate_bool)))
        elif 'error' in response.keys():
            print(print_util.color('[!] Error: ' + response['error'] + "obfuscate <True/False>"))

    @command
    def obfuscate_command(self, obfucation_type: str):
        """
        Set obfuscation technique to run for all future powershell commands run on all agents.

        Usage: obfuscate_command <obfucation_type>
        """
        options = {'obfuscate_command': obfucation_type}
        response = state.set_admin_options(options)

        # Return results and error message
        if 'success' in response.keys():
            print(print_util.color('[*] Set obfuscate_command to %s' % (obfucation_type)))
        elif 'error' in response.keys():
            print(print_util.color('[!] Error: ' + response['error']))

    @command
    def keyword_obfuscation(self, keyword: str, replacement: str = None):
        """
        Add key words to to be obfuscated from commands. Empire will generate a random word if no replacement word is provided. CANNOT BE USED WITH OBFUSCATE.

        Usage: keyword_obfuscation <keyword> [replacement]
        """
        options = {'keyword_obfuscation': keyword, 'keyword_replacement': replacement}
        response = state.set_admin_options(options)

        # Return results and error message
        if 'success' in response.keys():
            print(print_util.color('[*] Added keyword_obfuscation'))
        elif 'error' in response.keys():
            print(print_util.color('[!] Error: ' + response['error']))


admin_menu = AdminMenu()

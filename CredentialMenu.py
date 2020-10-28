import shlex
import string
import textwrap

from prompt_toolkit.completion import Completion
from terminaltables import SingleTable

from EmpireCliState import state
from utils import register_cli_commands, command


@register_cli_commands
class CredentialMenu(object):
    def __init__(self):
        self.selected_type = ''
        self.display_name = 'credentials'

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
            for word in self.autocomplete():
                if word.startswith(word_before_cursor):
                    yield Completion(word, start_position=-len(word_before_cursor), style="underline")

    def list(self) -> None:
        """
        Get running/available agents

        Usage: list
        """
        cred_list = list(map(
            lambda x: [x['ID'], x['credtype'], x['domain'], x['username'], x['host'], x['password']],
            state.get_creds()['creds']))
        cred_list.insert(0, ['ID', 'CredType', 'Domain', 'UserName', 'Host', 'Password/Hash'])
        table = SingleTable(cred_list)
        table.title = 'Credentials'
        table.inner_row_border = True
        print(table.table)

import shlex

from terminaltables import SingleTable

from EmpireCliState import state
from Menu import Menu
from utils import register_cli_commands


@register_cli_commands
class CredentialMenu(Menu):
    def __init__(self):
        super().__init__(display_name='credentials', selected='')

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


credential_menu = CredentialMenu()

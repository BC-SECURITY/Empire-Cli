from src.EmpireCliState import state
from src.menus.Menu import Menu
from src.utils import print_util, date_util
from src.utils import table_util
from src.utils.autocomplete_util import position_util
from src.utils.cli_util import register_cli_commands, command


@register_cli_commands
class AdminMenu(Menu):
    def __init__(self):
        super().__init__(display_name='admin', selected='')

    def autocomplete(self):
        return self._cmd_registry + super().autocomplete()

    def get_completions(self, document, complete_event, cmd_line, word_before_cursor):
        if position_util(cmd_line, 1, word_before_cursor):
            yield from super().get_completions(document, complete_event, cmd_line, word_before_cursor)

    def on_enter(self):
        self.user_id = state.get_user_me()['id']
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

    @command
    def user_list(self) -> None:
        """
        Display all Empire user accounts

        Usage: user_list
        """
        users_list = []

        for user in state.get_users()['users']:
            users_list.append([str(user['ID']), user['username'],
                               str(user['admin']), str(user['enabled']),
                               date_util.humanize_datetime(user['last_logon_time'])])

        users_list.insert(0, ['ID', 'Username', 'Admin', 'Enabled', 'Last Logon Time'])

        table_util.print_table(users_list, 'Users')

    @command
    def create_user(self, username: str, password: str):
        """
        Create user account for Empire

        Usage: create_user <username> <password>
        """
        options = {'username': username, 'password': password}
        response = state.create_user(options)

        # Return results and error message
        if 'success' in response.keys():
            print(print_util.color('[*] Added user: %s' % username))
        elif 'error' in response.keys():
            print(print_util.color('[!] Error: ' + response['error']))

    @command
    def disable_user(self, user_id: str):
        """
        Disable user account for Empire

        Usage: disable_user <user_id>
        """
        options = {'disable': 'True'}
        username = state.get_user(user_id)['username']
        response = state.disable_user(user_id, options)

        # Return results and error message
        if 'success' in response.keys():
            print(print_util.color('[*] Disabled user: %s' % username))
        elif 'error' in response.keys():
            print(print_util.color('[!] Error: ' + response['error']))

    @command
    def enable_user(self, user_id: str):
        """
        Enable user account for Empire

        Usage: enable_user <user_id>
        """
        options = {'disable': ''}
        username = state.get_user(user_id)['username']
        response = state.disable_user(user_id, options)

        # Return results and error message
        if 'success' in response.keys():
            print(print_util.color('[*] Enabled user: %s' % username))
        elif 'error' in response.keys():
            print(print_util.color('[!] Error: ' + response['error']))

    @command
    def notes(self) -> None:
        """
        Display your notes

        Usage: notes
        """
        self.user_notes = state.get_user_me()['notes']

        if not self.user_notes:
            print(print_util.color('[*] Notes are empty'))
        else:
            print(self.user_notes)

    @command
    def add_notes(self, add_user_notes: str):
        """
        Add user notes (use quotes)

        Usage: notes <add_user_notes>
        """
        self.user_notes = state.get_user_me()['notes']

        options = {'notes': self.user_notes + '\n' + add_user_notes}
        response = state.update_user_notes(self.user_id, options)

        if 'success' in response.keys():
            print(print_util.color('[*] Updated notes'))
        elif 'error' in response.keys():
            print(print_util.color('[!] Error: ' + response['error']))

    @command
    def clear_notes(self):
        """
        Clear user notes

        Usage: clear_notes
        """
        options = {'notes': ''}
        response = state.update_user_notes(self.user_id, options)

        if 'success' in response.keys():
            print(print_util.color('[*] Cleared notes'))
        elif 'error' in response.keys():
            print(print_util.color('[!] Error: ' + response['error']))


admin_menu = AdminMenu()

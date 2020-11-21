import sys
import threading

from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.patch_stdout import patch_stdout

from src.utils import print_util, table_util

from src.utils import table_util
from src.EmpireCliState import state
from src.menus.Menu import Menu
from src.utils.autocomplete_util import filtered_search_list, position_util
from src.utils.cli_utils import register_cli_commands, command

import socket
import select
import errno

@register_cli_commands
class ChatMenu(Menu):
    def __init__(self):
        super().__init__(display_name='chat', selected='')

    def autocomplete(self):
        return self._cmd_registry + super().autocomplete()

    def get_completions(self, document, complete_event, cmd_line, word_before_cursor):
        if position_util(cmd_line, 1, word_before_cursor):
            yield from super().get_completions(document, complete_event, cmd_line, word_before_cursor)

    def init(self):
        if 'chatserver' not in state.plugins:
            print(print_util.color('[!] Chatroom plugin not loaded'))
            return

        self.my_username = state.get_user_me()['username']
        state.sio.emit('chat/join', {'username': self.my_username, 'room': 'general'})

        # subscribe to chat notifications
        state.sio.on('chat/join', lambda data: print(print_util.color('[+] ' + data['message'])))
        state.sio.on('chat/leave', lambda data: print(print_util.color('[+] ' + data['message'])))
        state.sio.on('chat/message',
                     lambda data: print(print_util.color(data['username'], 'red') + ': ' + data['message']))
        return True

    def send_chat(self, text):
        state.sio.emit('chat/message', {'username': self.my_username, 'message': text, 'room': 'general'})

    def exit_room(self):
        state.sio.emit('chat/leave', {'username': self.my_username, 'room': 'general'})


chat_menu = ChatMenu()

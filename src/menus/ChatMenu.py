from src.EmpireCliState import state
from src.MenuState import menu_state
from src.menus.Menu import Menu
from src.utils import print_util
from src.utils.autocomplete_util import position_util
from src.utils.cli_util import register_cli_commands


@register_cli_commands
class ChatMenu(Menu):
    def __init__(self):
        super().__init__(display_name='chat', selected='')
        self.my_username = ''
        self.chat_cache = []

    def autocomplete(self):
        return self._cmd_registry + super().autocomplete()

    def get_completions(self, document, complete_event, cmd_line, word_before_cursor):
        if position_util(cmd_line, 1, word_before_cursor):
            yield from super().get_completions(document, complete_event, cmd_line, word_before_cursor)

    def get_prompt(self) -> str:
        return f"<b><ansigreen>{state.me['username']}</ansigreen></b>: "

    def on_connect(self):
        state.sio.on('chat/join', self.on_chat_join)
        state.sio.on('chat/leave', self.on_chat_leave)
        state.sio.on('chat/message', self.on_chat_message)
        state.sio.emit('chat/history')
        state.sio.emit('chat/join')

    def on_disconnect(self):
        state.sio.emit('chat/leave')

    def on_enter(self):
        print('Exit Chat Menu with ctrl-c')
        self.my_username = state.me['username']

        for message in self.chat_cache:
            print(message)

        self.chat_cache = []

        return True

    @staticmethod
    def is_chat_active():
        return menu_state.current_menu_name == 'ChatMenu'

    def on_chat_join(self, data):
        message = print_util.color('[+] ' + data['message'])
        if self.is_chat_active() == 'ChatMenu':
            print(message)
        else:
            self.chat_cache.append(message)

    def on_chat_leave(self, data):
        message = print_util.color('[+] ' + data['message'])
        if self.is_chat_active():
            print(message)
        else:
            self.chat_cache.append(message)

    def on_chat_message(self, data):
        if data['username'] != state.me['username'] or data.get('history') is True:
            if data['username'] == state.me['username']:
                message = print_util.color(data['username'], 'green') + ': ' + data['message']
                if self.is_chat_active():
                    print(message)
                else:
                    self.chat_cache.append(print_util.color(message))
            else:
                message = print_util.color(data['username'], 'red') + ': ' + data['message']
                if self.is_chat_active():
                    print(message)
                else:
                    self.chat_cache.append(message)

    def send_chat(self, text):
        state.sio.emit('chat/message', {'message': text})


chat_menu = ChatMenu()

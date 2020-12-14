from src.EmpireCliState import state
from src.menus.Menu import Menu
from src.utils import print_util
from src.utils.autocomplete_util import position_util
from src.utils.cli_util import register_cli_commands


@register_cli_commands
class ChatMenu(Menu):
    def __init__(self):
        super().__init__(display_name='chat', selected='')
        self.my_username = ''

    def autocomplete(self):
        return self._cmd_registry + super().autocomplete()

    def get_completions(self, document, complete_event, cmd_line, word_before_cursor):
        if position_util(cmd_line, 1, word_before_cursor):
            yield from super().get_completions(document, complete_event, cmd_line, word_before_cursor)

    def get_prompt(self) -> str:
        return f"<b><ansigreen>{state.me['username']}</ansigreen></b>: "

    def on_enter(self):
        self.my_username = state.me['username']

        # log into room and get chat history
        state.sio.emit('chat/join')
        state.sio.emit('chat/history')

        # subscribe to chat notifications
        state.sio.on('chat/join', lambda data: print(print_util.color('[+] ' + data['message'])))
        state.sio.on('chat/leave', lambda data: print(print_util.color('[+] ' + data['message'])))
        state.sio.on('chat/message', self.on_message)
        return True

    def on_leave(self, **kwargs) -> bool:
        self.exit_room()
        return True

    def on_message(self, data):
        if data['username'] != state.me['username'] or data.get('history') is True:
            if data['username'] == state.me['username']:
                print(print_util.color(data['username'], 'green') + ': ' + data['message'])
            else:
                print(print_util.color(data['username'], 'red') + ': ' + data['message'])

    def send_chat(self, text):
        state.sio.emit('chat/message', {'message': text})

    def exit_room(self):
        state.sio.emit('chat/leave')


chat_menu = ChatMenu()

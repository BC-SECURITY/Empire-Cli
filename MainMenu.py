import shlex

from prompt_toolkit.completion import Completion

from EmpireCliConfig import empire_config
from EmpireCliState import state
from utils import register_cli_commands, command


@register_cli_commands
class MainMenu(object):
    def __init__(self):
        self.display_name = ''

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()
        try:
            cmd_line = list(map(lambda s: s.lower(), shlex.split(document.current_line)))
            # print(cmd_line)
        except ValueError:
            pass
        else:
            if len(cmd_line) > 1 and cmd_line[0] == 'connect' and cmd_line[1] in ['-c', '--connect']:
                for server in empire_config.yaml.get('servers', []):
                    yield Completion(server, start_position=-len(word_before_cursor))
            else:
                for word in self.autocomplete():
                    if word.startswith(word_before_cursor):
                        yield Completion(word, start_position=-len(word_before_cursor))

    def autocomplete(self):
        return [
            'connect',
            'disconnect',
            'exit',
            'help',
            'listeners',
            'agents',
            'modules',
            'users',
            'uselistener',
            'usestager',
            'plugins'
        ]

    @command
    def connect(self, host: str, config: bool = False, port: int = 1337, socketport: int = 5000, username: str = None, password: str = None) -> None:
        """
        Connect to empire instance

        Usage: connect [--config | -c] <host> [--port=<p>] [--socketport=<sp>] [--username=<u>] [--password=<pw>]

        Options:
            host               The url for the empire server or the name of a server config from config.yaml
            --config -c        When true, host is a server name from config.yaml [default: False]
            --port=<p>         Port number for empire server. [default: 1337]
            --socketport=<sp>  Port number for empire socketio server. [default: 5000]
            --username=<u>     Username for empire. if not provided, will attempt to pull from yaml
            --password=<pw>    Password for empire. if not provided, will attempt to pull from yaml
        """
        if config is True:
            # Check for name in yaml
            server: dict = empire_config.yaml.get('servers').get(host)
            if not server:
                print(f'Could not find server in config.yaml for {host}')
            state.connect(server['host'], server['port'], server['socketport'], server['username'], server['password'])
        else:
            state.connect(host, port, socketport, username, password)

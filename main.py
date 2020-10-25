import re
import shlex
from typing import get_type_hints

import urllib3
from docopt import docopt
from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.patch_stdout import patch_stdout

from AgentMenu import AgentMenu
from EmpireCliState import state
from ListenerMenu import ListenerMenu
from MainMenu import MainMenu
from UseListenerMenu import UseListenerMenu
from UseStagerMenu import UseStagerMenu
from UseModuleMenu import UseModuleMenu
from InteractMenu import InteractMenu
from ShellMenu import ShellMenu
from CredentialMenu import CredentialMenu

# todo probably put a prop in config.yaml to suppress this (from self-signed certs)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MyCustomCompleter(Completer):
    def __init__(self, empire_cli):
        self.empire_cli = empire_cli

    def get_completions(self, document, complete_event):
        #word_before_cursor = document.get_word_before_cursor()
        #if not state.connected:
        #   yield Completion('connect', start_position=-len(word_before_cursor))

        cmd_line = list(map(lambda s: s.lower(), shlex.split(document.current_line)))
        if len(cmd_line) > 0:
            if cmd_line[0] in ['uselistener']:
                return self.empire_cli.menus['UseListenerMenu'].get_completions(document, complete_event)
            if cmd_line[0] in ['usestager']:
                return self.empire_cli.menus['UseStagerMenu'].get_completions(document, complete_event)
            if cmd_line[0] in ['usemodule']:
                return self.empire_cli.menus['UseModuleMenu'].get_completions(document, complete_event)
            if cmd_line[0] in ['interact']:
                return self.empire_cli.menus['InteractMenu'].get_completions(document, complete_event)
            if cmd_line[0] in ['credentials']:
                return self.empire_cli.menus['CredentialMenu'].get_completions(document, complete_event)

        return self.empire_cli.current_menu.get_completions(document, complete_event)


class EmpireCli(object):

    def __init__(self) -> None:
        self.completer = MyCustomCompleter(self)
        self.menus = {
            'MainMenu': MainMenu(),
            'ListenerMenu': ListenerMenu(),
            'UseListenerMenu': UseListenerMenu(),
            'UseStagerMenu': UseStagerMenu(),
            'AgentMenu': AgentMenu(),
            'UseModuleMenu': UseModuleMenu(),
            'InteractMenu': InteractMenu(),
            'ShellMenu': ShellMenu(),
            'CredentialMenu': CredentialMenu(),
        }
        self.current_menu = self.menus['MainMenu']
        self.previous_menu = self.menus['MainMenu']

    def autocomplete(self):
        return self.current_menu.autocomplete()

    def bottom_toolbar(self):
        # TODO This will read number of listeners, agents, etc from the state
        return HTML('Connected to <b><style bg="ansired">https://localhost:1337</style></b>. 6 agents.')

    @staticmethod
    def strip(options):
        return {re.sub('[^A-Za-z0-9 _]+', '', k): v for k, v in options.items()}

    def main(self):
        # Create some history first. (Easy for testing.)
        history = InMemoryHistory()
        history.append_string("help")
        history.append_string('uselistener http')
        history.append_string('listeners')
        history.append_string("main")
        history.append_string("connect -c localhost")

        print('Welcome to Empire!')
        print("Use the 'connect' command to connect to your Empire server.")
        print("connect localhost will connect to a local empire instance with all the defaults")
        print("including the default username and password.")

        session = PromptSession(
            history=history,
            auto_suggest=AutoSuggestFromHistory(),
            enable_history_search=True,
            completer=self.completer,
            bottom_toolbar=self.bottom_toolbar
        )

        while True:
            try:
                with patch_stdout():
                    text = session.prompt(HTML((f"<ansiblue>{self.current_menu.display_name}</ansiblue> > ")))
                # cmd_line = list(map(lambda s: s.lower(), shlex.split(text)))
                # TODO what to do about case sensitivity for parsing options.
                    cmd_line = list(shlex.split(text))
            except KeyboardInterrupt:
                continue  # Control-C pressed. Try again.
            except EOFError:
                break  # Control-D pressed.

            if len(cmd_line) == 0:
                continue
            if not state.connected and not cmd_line[0] == 'connect':
                continue

            # Switch Menus
            if text == 'main':
                self.current_menu = self.menus['MainMenu']
            elif text == 'listeners':
                self.current_menu = self.menus['ListenerMenu']
                self.current_menu.list()
            elif cmd_line[0] == 'uselistener' and len(cmd_line) > 1:
                if len(list(filter(lambda x: x == cmd_line[1], state.listener_types['types']))) > 0:
                    # todo utilize the command decorator?
                    self.current_menu = self.menus['UseListenerMenu']
                    self.current_menu.use(cmd_line[1])
                else:
                    print(f'No module {cmd_line[1]}')
            elif cmd_line[0] == 'usestager' and len(cmd_line) > 1:
                if len(list(filter(lambda x: x == cmd_line[1], state.stager_types['types']))) > 0:
                    # todo utilize the command decorator?
                    self.current_menu = self.menus['UseStagerMenu']
                    self.current_menu.use(cmd_line[1])
                else:
                    print(f'No module {cmd_line[1]}')
            elif text == 'stagers':
                self.current_menu = self.menus['StagerMenu']
            elif text == 'agents':
                self.current_menu = self.menus['AgentMenu']
                self.current_menu.list()
            elif cmd_line[0] == 'usemodule' and len(cmd_line) > 1:
                if len(list(filter(lambda x: x == cmd_line[1], state.module_types['types']))) > 0:
                    # todo utilize the command decorator?
                    previous_menu = self.current_menu
                    self.current_menu = self.menus['UseModuleMenu']
                    self.current_menu.use(cmd_line[1])
                    if previous_menu == self.menus['InteractMenu']:
                        self.current_menu.set('Agent', previous_menu.selected_type)
                        self.current_menu.info()
                else:
                    print(f'No module {cmd_line[1]}')
            elif cmd_line[0] == 'interact' and len(cmd_line) > 1:
                if len(list(filter(lambda x: x == cmd_line[1], state.agent_types['types']))) > 0:
                    # todo utilize the command decorator?
                    self.current_menu = self.menus['InteractMenu']
                    self.current_menu.use(cmd_line[1])
                else:
                    print(f'No module {cmd_line[1]}')
            elif text == 'shell':
                # todo utilize the command decorator?
                self.previous_menu = self.current_menu
                if self.previous_menu == self.menus['InteractMenu']:
                    self.current_menu = self.menus['ShellMenu']
                    self.current_menu.selected_type = self.previous_menu.selected_type
                    self.current_menu.use(self.current_menu.selected_type)
                else:
                    pass
            elif self.current_menu == self.menus['ShellMenu']:
                if text == 'exit':
                    self.current_menu = self.previous_menu
                else:
                    self.current_menu.shell(self.current_menu.selected_type, text)
            elif text == 'credentials':
                self.current_menu = self.menus['CredentialMenu']
                self.current_menu.list()
            elif cmd_line[0] == 'report':
                if len(cmd_line) > 1:
                    state.generate_report(cmd_line[1])
                else:
                    state.generate_report('')
            else:
                func = None
                try:
                    func = getattr(self.current_menu if hasattr(self.current_menu, cmd_line[0]) else self, cmd_line[0])
                except:
                    pass

                if func:
                    try:
                        args = self.strip(docopt(
                            func.__doc__,
                            argv=cmd_line[1:]
                        ))
                        # ST does this in the @command decorator
                        new_args = {}
                        # todo casting for typehinted values
                        for key, hint in get_type_hints(func).items():
                            # if args.get(key) is not None:
                            if key is not 'return':
                                new_args[key] = args[key]
                        print(new_args)
                        func(**new_args)
                    except Exception as e:
                        print(e)
                        pass


if __name__ == "__main__":
    empire = EmpireCli()
    empire.main()

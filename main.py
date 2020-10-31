import re
import shlex
from typing import get_type_hints, Dict

import urllib3
from docopt import docopt
from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.patch_stdout import patch_stdout

import Menu
from AgentMenu import agent_menu
from CredentialMenu import credential_menu
from EmpireCliState import state
from InteractMenu import interact_menu
from ListenerMenu import listener_menu
from MainMenu import main_menu
from PluginMenu import plugin_menu
from ShellMenu import shell_menu
from UseListenerMenu import use_listener_menu
from UseModuleMenu import use_module_menu
from UsePluginMenu import use_plugin_menu
from UseStagerMenu import use_stager_menu

# todo probably put a prop in config.yaml to suppress this (from self-signed certs)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class MyCustomCompleter(Completer):
    def __init__(self, empire_cli):
        self.empire_cli = empire_cli

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()
        if not state.connected:
            yield Completion('connect', start_position=-len(word_before_cursor))
            return

        cmd_line = list(map(lambda s: s.lower(), shlex.split(document.current_line)))
        if len(cmd_line) > 0:
            if cmd_line[0] in ['uselistener']:
                yield from self.empire_cli.menus['UseListenerMenu'].get_completions(document, complete_event)
            elif cmd_line[0] in ['usestager']:
                yield from self.empire_cli.menus['UseStagerMenu'].get_completions(document, complete_event)
            elif cmd_line[0] in ['usemodule']:
                yield from self.empire_cli.menus['UseModuleMenu'].get_completions(document, complete_event)
            elif cmd_line[0] in ['interact']:
                yield from self.empire_cli.menus['InteractMenu'].get_completions(document, complete_event)
            elif cmd_line[0] in ['useplugin']:
                yield from self.empire_cli.menus['UsePluginMenu'].get_completions(document, complete_event)
            else:
                yield from self.empire_cli.current_menu.get_completions(document, complete_event)
        else:
            yield from self.empire_cli.current_menu.get_completions(document, complete_event)


class EmpireCli(object):

    def __init__(self) -> None:
        self.completer = MyCustomCompleter(self)
        self.menus: Dict[Menu] = {
            'MainMenu': main_menu,
            'ListenerMenu': listener_menu,
            'UseListenerMenu': use_listener_menu,
            'UseStagerMenu': use_stager_menu,
            'AgentMenu': agent_menu,
            'UseModuleMenu': use_module_menu,
            'InteractMenu': interact_menu,
            'ShellMenu': shell_menu,
            'CredentialMenu': credential_menu,
            'PluginMenu': plugin_menu,
            'UsePluginMenu': use_plugin_menu,

        }
        self.current_menu = self.menus['MainMenu']
        self.previous_menu = self.menus['MainMenu']
        self.menu_history = [self.menus['MainMenu']]

    @staticmethod
    def bottom_toolbar():
        if state.connected:
            return HTML(f'Connected to {state.host}:{state.port}. {len(state.agents)} agents.')
        else:
            return ''

    @staticmethod
    def strip(options):
        return {re.sub('[^A-Za-z0-9 _]+', '', k): v for k, v in options.items()}

    def change_menu(self, menu: Menu):
        self.current_menu = menu
        self.menu_history.append(menu)
        menu.init()

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
            # auto_suggest=AutoSuggestFromHistory(),
            # enable_history_search=True,
            completer=self.completer,
            complete_in_thread=True,
            # complete_while_typing=True,
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
                self.change_menu(self.menus['MainMenu'])
            elif text == 'listeners':
                self.change_menu(self.menus['ListenerMenu'])
            elif text == 'agents':
                self.change_menu(self.menus['AgentMenu'])
            elif text == 'credentials':
                self.change_menu(self.menus['CredentialMenu'])
            elif text == 'plugins':
                self.change_menu(self.menus['PluginMenu'])
            elif cmd_line[0] == 'uselistener' and len(cmd_line) > 1:
                if cmd_line[1] in state.listener_types:
                    # todo utilize the command decorator? Call use as part of init?
                    self.menus['UseListenerMenu'].use(cmd_line[1])
                    self.change_menu(self.menus['UseListenerMenu'])
                else:
                    print(f'No module {cmd_line[1]}')
            elif cmd_line[0] == 'usestager' and len(cmd_line) > 1:
                if cmd_line[1] in state.stagers:
                    # todo utilize the command decorator?
                    self.menus['UseStagerMenu'].use(cmd_line[1])
                    self.change_menu(self.menus['UseStagerMenu'])
                else:
                    print(f'No module {cmd_line[1]}')
            elif cmd_line[0] == 'usemodule' and len(cmd_line) > 1:
                if cmd_line[1] in state.modules:
                    # todo utilize the command decorator?
                    self.previous_menu = self.current_menu
                    self.change_menu(self.menus['UseModuleMenu'])
                    # todo can we call use in change_menu?
                    self.current_menu.use(cmd_line[1])
                    # todo if we track menus in the state could the menu do this itself in init?
                    if self.previous_menu == self.menus['InteractMenu']:
                        self.current_menu.set('Agent', self.previous_menu.selected_type)
                        self.current_menu.info()
                else:
                    print(f'No module {cmd_line[1]}')

            elif cmd_line[0] == 'interact' and len(cmd_line) > 1:
                if cmd_line[1] in state.agents:
                    # todo utilize the command decorator?
                    self.menus['InteractMenu'].use(cmd_line[1])
                    self.change_menu(self.menus['InteractMenu'])
                else:
                    print(f'No module {cmd_line[1]}')

            elif text == 'shell':
                # todo utilize the command decorator?
                self.previous_menu = self.current_menu
                if self.previous_menu == self.menus['InteractMenu']:
                    self.current_menu = self.menus['ShellMenu']
                    self.menu_history.append(self.current_menu)
                    self.current_menu.selected = self.previous_menu.selected
                    self.current_menu.use(self.current_menu.selected)
                else:
                    pass

            elif self.current_menu == self.menus['ShellMenu']:
                if text == 'exit':
                    self.current_menu = self.previous_menu
                else:
                    self.current_menu.shell(self.current_menu.selected_type, text)
            elif cmd_line[0] == 'report':
                if len(cmd_line) > 1:
                    state.generate_report(cmd_line[1])
                else:
                    state.generate_report('')

            elif cmd_line[0] == 'useplugin' and len(cmd_line) > 1:
                if cmd_line[1] in state.plugins:
                    # todo utilize the command decorator?
                    self.menus['UsePluginMenu'].use(cmd_line[1])
                    self.change_menu(self.menus['UsePluginMenu'])
                else:
                    print(f'No module {cmd_line[1]}')

            elif text == 'back':
                if self.current_menu != self.menus['MainMenu']:
                    del self.menu_history[-1]
                    self.current_menu = self.menu_history[-1]

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
                        # todo casting for type hinted values
                        for key, hint in get_type_hints(func).items():
                            # if args.get(key) is not None:
                            if key is not 'return':
                                new_args[key] = args[key]
                        #print(new_args)
                        func(**new_args)
                    except Exception as e:
                        print(e)
                        pass


if __name__ == "__main__":
    empire = EmpireCli()
    empire.main()

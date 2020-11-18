import os
import re
import shlex
import sys
import threading
import time
from typing import get_type_hints, Dict

import urllib3
from docopt import docopt
from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.completion import Completer
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.patch_stdout import patch_stdout

from ShortcutHandler import shortcut_handler
from utils import print_util, table_util
import Menu

from AgentMenu import agent_menu
from CredentialMenu import credential_menu
from EmpireCliConfig import empire_config
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


class MyCustomCompleter(Completer):
    def __init__(self, empire_cli):
        self.empire_cli = empire_cli

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor(WORD=True)

        try:
            cmd_line = list(map(lambda s: s.lower(), shlex.split(document.current_line)))
            if len(cmd_line) == 0:
                cmd_line.append('')
        except ValueError:
            pass
        else:
            if not state.connected:
                yield from self.empire_cli.menus['MainMenu'].get_completions(document, complete_event, cmd_line,
                                                                             word_before_cursor)
            # These commands should be accessible anywhere.
            elif cmd_line[0] in ['uselistener']:
                yield from self.empire_cli.menus['UseListenerMenu'].get_completions(document, complete_event, cmd_line,
                                                                                    word_before_cursor)
            elif cmd_line[0] in ['usestager']:
                yield from self.empire_cli.menus['UseStagerMenu'].get_completions(document, complete_event, cmd_line,
                                                                                  word_before_cursor)
            elif cmd_line[0] in ['usemodule']:
                yield from self.empire_cli.menus['UseModuleMenu'].get_completions(document, complete_event, cmd_line,
                                                                                  word_before_cursor)
            elif cmd_line[0] in ['interact']:
                yield from self.empire_cli.menus['InteractMenu'].get_completions(document, complete_event, cmd_line,
                                                                                 word_before_cursor)
            elif cmd_line[0] in ['useplugin']:
                yield from self.empire_cli.menus['UsePluginMenu'].get_completions(document, complete_event, cmd_line,
                                                                                  word_before_cursor)
            else:
                # Menu specific commands
                yield from self.empire_cli.current_menu.get_completions(document, complete_event, cmd_line,
                                                                        word_before_cursor)


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

    def change_menu(self, menu: Menu, **kwargs):
        if menu.init(**kwargs):
            self.current_menu = menu
            self.menu_history.append(menu)

    def main(self):
        if empire_config.yaml.get('suppress-self-cert-warning', True):
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Create some history first. (Easy for testing.)
        history = InMemoryHistory()
        history.append_string("help")
        history.append_string('uselistener http')
        history.append_string('listeners')
        history.append_string("main")
        history.append_string("connect -c localhost")

        print_util.loading()
        print("\n")
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
            bottom_toolbar=self.bottom_toolbar,
            #swap_light_and_dark_colors=True,
            #mouse_support=True
        )

        while True:
            try:
                with patch_stdout():
                    t = threading.Thread(target=self.update_in_bg, args=[session])
                    t.start()
                    text = session.prompt(HTML(self.current_menu.get_prompt()), refresh_interval=None)
                    # cmd_line = list(map(lambda s: s.lower(), shlex.split(text)))
                    # TODO what to do about case sensitivity for parsing options.
                    cmd_line = list(shlex.split(text))
            except KeyboardInterrupt:
                print(print_util.color("[!] Type exit to quit"))
                continue  # Control-C pressed. Try again.
            except EOFError:
                break  # Control-D pressed.

            if len(cmd_line) == 0:
                continue
            if not state.connected and not cmd_line[0] == 'connect':
                if cmd_line[0] == 'exit':
                    choice = input(print_util.color("[>] Exit? [y/N] ", "red"))
                    if choice.lower() == "y":
                        sys.exit()
                    else:
                        continue
                else:
                    continue

            # Switch Menus
            if text == 'main':
                print_util.title(state.empire_version, len(state.modules), len(state.listeners), len(state.agents))
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
                    self.change_menu(self.menus['UseListenerMenu'], selected=cmd_line[1])
                else:
                    print(f'No module {cmd_line[1]}')
            elif cmd_line[0] == 'usestager' and len(cmd_line) > 1:
                if cmd_line[1] in state.stagers:
                    self.change_menu(self.menus['UseStagerMenu'], selected=cmd_line[1])
                else:
                    print(f'No module {cmd_line[1]}')
            elif cmd_line[0] == 'interact' and len(cmd_line) > 1:
                if cmd_line[1] in state.agents:
                    self.change_menu(self.menus['InteractMenu'], selected=cmd_line[1])
                else:
                    print(f'No module {cmd_line[1]}')
            elif cmd_line[0] == 'useplugin' and len(cmd_line) > 1:
                if cmd_line[1] in state.plugins:
                    self.change_menu(self.menus['UsePluginMenu'], selected=cmd_line[1])
                else:
                    print(f'No module {cmd_line[1]}')
            elif cmd_line[0] == 'usemodule' and len(cmd_line) > 1:
                if cmd_line[1] in state.modules:
                    if self.current_menu == self.menus['InteractMenu']:
                        self.change_menu(self.menus['UseModuleMenu'], selected=cmd_line[1],
                                         agent=self.current_menu.selected)
                    else:
                        self.change_menu(self.menus['UseModuleMenu'], selected=cmd_line[1])
                else:
                    print(f'No module {cmd_line[1]}')
            elif text == 'shell':
                if self.current_menu == self.menus['InteractMenu']:
                    self.change_menu(self.menus['ShellMenu'], selected=self.current_menu.selected)
                else:
                    pass
            elif self.current_menu == self.menus['ShellMenu']:
                if text == 'exit':
                    self.change_menu(self.menus['InteractMenu'], selected=self.current_menu.selected)
                else:
                    self.current_menu.shell(self.current_menu.selected, text)
            elif cmd_line[0] == 'report':
                if len(cmd_line) > 1:
                    state.generate_report(cmd_line[1])
                else:
                    state.generate_report('')
            elif text == 'back':
                if self.current_menu != self.menus['MainMenu']:
                    del self.menu_history[-1]
                    self.current_menu = self.menu_history[-1]
            elif text == 'exit':
                choice = input(print_util.color("[>] Exit? [y/N] ", "red"))
                if choice.lower() == "y":
                    break
                else:
                    pass
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
                        new_args = {}
                        # todo casting for type hinted values?
                        for key, hint in get_type_hints(func).items():
                            # if args.get(key) is not None:
                            if key != 'return':
                                new_args[key] = args[key]
                        # print(new_args)
                        func(**new_args)
                    except Exception as e:
                        print(e)
                        pass
                    except SystemExit as e:
                        pass
                elif not func and self.current_menu == self.menus['InteractMenu']:
                    if cmd_line[0] in shortcut_handler.get_names(self.menus['InteractMenu'].agent_language):
                        self.current_menu.execute_shortcut(cmd_line[0], cmd_line[1:])

        return

    def update_in_bg(self, session: PromptSession):
        while True:
            time.sleep(3)
            session.message = HTML(self.current_menu.get_prompt())
            session.app.invalidate()


if __name__ == "__main__":
    try:
        empire = EmpireCli()
        empire.main()
    finally:
        # TODO: There has to be a better way to exit but sys.exit() is getting stuck on something
        os._exit(0)

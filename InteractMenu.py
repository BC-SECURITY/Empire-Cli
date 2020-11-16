import base64
import json
import os
import textwrap
import threading
import time
from typing import List, Optional

from prompt_toolkit.completion import Completion

from EmpireCliState import state
from Menu import Menu
from Shortcut import Shortcut
from ShortcutHandler import shortcut_handler
from utils import print_util, table_util
from utils.autocomplete_utils import filtered_search_list, position_util
from utils.cli_utils import register_cli_commands, command


@register_cli_commands
class InteractMenu(Menu):
    def __init__(self):
        super().__init__(display_name='', selected='')
        self.agent_options = {}
        self.agent_language = ''

    def autocomplete(self):
        return self._cmd_registry + \
               super().autocomplete() + \
               shortcut_handler.get_names(self.agent_language)

    def get_completions(self, document, complete_event, cmd_line, word_before_cursor):
        if cmd_line[0] in ['interact'] and position_util(cmd_line, 2, word_before_cursor):
            for agent in filtered_search_list(word_before_cursor, state.agents.keys()):
                yield Completion(agent, start_position=-len(word_before_cursor))
        elif position_util(cmd_line, 1, word_before_cursor):
            yield from super().get_completions(document, complete_event, cmd_line, word_before_cursor)
        elif cmd_line[0] in shortcut_handler.get_names(self.agent_language):
            position = len(cmd_line)
            shortcut = shortcut_handler.get(self.agent_language, cmd_line[0])
            params = shortcut.get_dynamic_param_names()
            if position - 1 < len(params):
                if params[position - 1].lower() == 'listener':
                    for listener in filtered_search_list(word_before_cursor, state.listeners.keys()):
                        yield Completion(listener, start_position=-len(word_before_cursor))
                if params[position - 1].lower() == 'agent':
                    for agent in filtered_search_list(word_before_cursor, state.agents.keys()):
                        yield Completion(agent, start_position=-len(word_before_cursor))

    def init(self, **kwargs) -> bool:
        if 'selected' not in kwargs:
            return False
        else:
            self.use(kwargs['selected'])
            return True

    def get_prompt(self) -> str:
        joined = '/'.join([self.display_name, self.selected]).strip('/')
        return f"(Empire: <ansired>{joined}</ansired>) > "

    # todo is this the same exact code in the other menus?
    def tasking_id_returns(self, agent_name, task_id: int):
        """
        Polls and prints tasking data for taskID

        Usage: tasking_id_returns <agent_name> <task_id>
        """
        # todo: there must be a better way to do this with notifications
        # todo: add a timeout value
        # Set previous results to current results to avoid a lot of old data
        status_result = False

        while not status_result:
            try:
                results = state.get_agent_result(agent_name)['results'][0]['AgentResults'][task_id - 1]
                if results['results'] is not None:
                    print(print_util.color('[*] Task ' + str(results['taskID']) + " results received"))
                    print(print_util.color(results['results']))
                    status_result = True
            except:
                pass
            time.sleep(1)

    def use(self, agent_name: str) -> None:
        """
        Use the selected agent

        Usage: use <agent_name>
        """
        if agent_name in state.agents.keys():
            self.selected = agent_name
            self.agent_options = state.agents[agent_name]  # todo rename agent_options
            self.agent_language = self.agent_options['language']

    @command
    def shell(self, shell_cmd: str) -> None:
        """
        Tasks an the specified agent to execute a shell command.

        Usage: shell <shell_cmd>
        """
        response = state.agent_shell(self.selected, shell_cmd)
        print(print_util.color('[*] Tasked ' + self.selected + ' to run Task ' + str(response['taskID'])))

        # todo can we use asyncio?
        agent_return = threading.Thread(target=self.tasking_id_returns, args=[self.selected, response['taskID']])
        agent_return.start()

    @command
    def upload(self, local_file_directory: str, destination_file_name: str) -> None:
        """
        Tasks an the specified agent to upload a file.

        Usage: upload <local_file_directory> [destination_file_name]
        """
        file_name = os.path.basename(local_file_directory)
        open_file = open(local_file_directory, 'rb')
        file_data = base64.b64encode(open_file.read())

        if destination_file_name:
            file_name = destination_file_name

        response = state.agent_upload_file(self.selected, file_name, file_data)
        print(print_util.color('[*] Tasked ' + self.selected + ' to run Task ' + str(response['taskID'])))
        agent_return = threading.Thread(target=self.tasking_id_returns, args=[self.selected, response['taskID']])
        agent_return.start()

    @command
    def download(self, file_name: str) -> None:
        """
        Tasks an the specified agent to download a file.

        Usage: download <file_name>
        """
        response = state.agent_download_file(self.selected, file_name)
        print(print_util.color('[*] Tasked ' + self.selected + ' to run Task ' + str(response['taskID'])))
        agent_return = threading.Thread(target=self.tasking_id_returns, args=[self.selected, response['taskID']])
        agent_return.start()

    @command
    def info(self) -> None:
        """
        Display agent info.

        Usage: info
        """
        agent_list = []
        for key, value in self.agent_options.items():
            if isinstance(value, int):
                value = str(value)
            if value is None:
                value = ''
            if key not in ['taskings', 'results']:
                temp = [key, '\n'.join(textwrap.wrap(str(value), width=45))]
                agent_list.append(temp)

        table_util.print_table(agent_list, 'Agent Options')

    @command
    def help(self):
        """
        Display the help menu for the current menu

        Usage: help
        """
        help_list = []
        for name in self._cmd_registry:
            try:
                description = print_util.text_wrap(getattr(self, name).__doc__.split('\n')[1].lstrip(), width=35)
                usage = print_util.text_wrap(getattr(self, name).__doc__.split('\n')[3].lstrip()[7:], width=35)
                help_list.append([name, description, usage])
            except:
                continue

        for name, shortcut in shortcut_handler.shortcuts['python'].items():
            try:
                description = shortcut.get_help_description()
                usage = shortcut.get_usage_string()
                help_list.append([name, description, usage])
            except:
                continue
        help_list.insert(0, ['Name', 'Description', 'Usage'])
        table_util.print_table(help_list, 'Help Options')

    def execute_shortcut(self, command_name: str, params: List[str]):
        shortcut: Shortcut = shortcut_handler.get(self.agent_language, command_name)

        if not shortcut:
            return None
        if not len(params) == len(shortcut.get_dynamic_param_names()):
            return None  # todo log message
        module_options = dict.copy(state.modules[shortcut.module]['options'])

        post_body = {}

        for i, shortcut_param in enumerate(shortcut.get_dynamic_params()):
            if shortcut_param.name in module_options:
                post_body[shortcut_param.name] = params[i]

        # TODO Still haven't figured out other data types. Right now everything is a string.
        #  Which I think is how it is in the old cli
        for key, value in module_options.items():
            if key in shortcut.get_dynamic_param_names():
                continue
            elif key in shortcut.get_static_param_names():
                post_body[key] = shortcut.get_param(key).value
            else:
                post_body[key] = module_options[key]['Value']
        post_body['Agent'] = self.selected
        response = state.execute_module(shortcut.module, post_body)
        if 'success' in response.keys():
            print(print_util.color(
                '[*] Tasked ' + self.selected + ' to run Task ' + str(response['taskID'])))
            agent_return = threading.Thread(target=self.tasking_id_returns,
                                            args=[self.selected, response['taskID']])
            agent_return.start()
        elif 'error' in response.keys():
            print(print_util.color('[!] Error: ' + response['error']))


interact_menu = InteractMenu()

if __name__ == "__main__":
    interact_menu.agent_language = 'python'
    state.modules = {}
    state.modules['python/collection/osx/screenshot'] = {}
    state.modules['python/collection/osx/screenshot']['options'] = {'SavePath': '/tmp/out.png'}
    interact_menu.execute_shortcut('sc', ['http1', '/tmp', 'agent'])

import base64
import os
import shlex
import string
import textwrap
import threading
import time

from prompt_toolkit.completion import Completion
from terminaltables import SingleTable

import print_util
import table_util
from EmpireCliConfig import empire_config
from EmpireCliState import state
from Menu import Menu
from utils import register_cli_commands, command, position_util, filtered_search_list


@register_cli_commands
class InteractMenu(Menu):
    def __init__(self):
        super().__init__(display_name='', selected='')
        self.agent_options = {}
        self.shortcuts = empire_config.yaml.get('shortcuts', {})
        self.agent_language = ''

    def autocomplete(self):
        return self._cmd_registry +\
               super().autocomplete() +\
               list(map(lambda x: x['name'], self.shortcuts.get(self.agent_language, [])))

    def get_completions(self, document, complete_event, cmd_line, word_before_cursor):
        if cmd_line[0] in ['interact'] and position_util(cmd_line, 2, word_before_cursor):
            for agent in filtered_search_list(word_before_cursor, state.agents.keys()):
                yield Completion(agent, start_position=-len(word_before_cursor))
        elif position_util(cmd_line, 1, word_before_cursor):
            yield from super().get_completions(document, complete_event, cmd_line, word_before_cursor)

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

    @command
    def use(self, agent_name: str) -> None:
        """
        Use the selected agent

        Usage: use <agent_name>
        """
        if agent_name in state.agents.keys():
            self.selected = agent_name
            self.display_name = self.selected
            self.agent_options = state.agents[agent_name]
            self.agent_language = self.agent_options['language']

    @command
    def shell(self, shell_cmd: str) -> None:
        """
        Tasks an the specified agent to execute a shell command.

        Usage: shell <shell_cmd>
        """
        response = state.agent_shell(self.selected_type, shell_cmd)
        print(print_util.color('[*] Tasked ' + self.selected_type + ' to run Task ' + str(response['taskID'])))

        # todo can we use asyncio?
        agent_return = threading.Thread(target=self.tasking_id_returns, args=[self.selected_type, response['taskID']])
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
        response = state.agent_download_file(self.selected_type, file_name)
        print(print_util.color('[*] Tasked ' + self.selected_type + ' to run Task ' + str(response['taskID'])))
        agent_return = threading.Thread(target=self.tasking_id_returns, args=[self.selected_type, response['taskID']])
        agent_return.start()

    @command
    def sysinfo(self) -> None:
        """
        Tasks an the specified agent to execute Get-Sysinfo.

        Usage: sysinfo
        """
        state.agent_shell(self.selected, 'Get-Sysinfo')

    @command
    def info(self) -> None:
        """
        Display agent info.

        Usage: info
        """
        # todo: the spacing looks off on the table
        agent_list = []
        for key, value in self.agent_options.items():
            if isinstance(value, int):
                value = str(value)
            if value is None:
                value = ''
            temp = [key, value]
            agent_list.append(temp)

        table_util.print_table(agent_list, 'Agent Options')

    def execute_shortcut(self, command_name: str):
        shortcuts = {x['name']: x for x in self.shortcuts.get(self.agent_language, [])}
        shortcut = shortcuts.get(command_name)
        if not shortcut:
            return None
        module_options = dict.copy(state.modules[shortcut['module']]['options'])

        post_body = {}
        for key, value in module_options.items():
            if key in shortcut.get('params', {}):
                post_body[key] = shortcut['params'][key]
            else:
                post_body[key] = module_options[key]['Value']
        post_body['Agent'] = self.selected
        state.execute_module(shortcut['module'], post_body)


interact_menu = InteractMenu()

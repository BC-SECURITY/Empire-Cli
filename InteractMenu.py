import base64
import os
import textwrap
import threading
import time

from prompt_toolkit.completion import Completion

from utils import print_util, table_util
from EmpireCliState import state
from Menu import Menu
from utils.autocomplete_utils import filtered_search_list, position_util
from utils.cli_utils import register_cli_commands, command


@register_cli_commands
class InteractMenu(Menu):
    def __init__(self):
        super().__init__(display_name='', selected='')
        self.agent_options = {}

    def autocomplete(self):
        return self._cmd_registry + super().autocomplete()

    def get_completions(self, document, complete_event, cmd_line, word_before_cursor):
        if cmd_line[0] in ['interact'] and position_util(cmd_line, 2, word_before_cursor):
            for agent in filtered_search_list(word_before_cursor, state.agents.keys()):
                yield Completion(agent, start_position=-len(word_before_cursor))
        elif position_util(cmd_line, 1, word_before_cursor):
            yield from super().get_completions(document, complete_event, cmd_line, word_before_cursor)

    def init(self, **kwargs) -> bool:
        if 'selected' not in kwargs:
            return False
        else:
            self.use(kwargs['selected'])
            return True

    def get_prompt(self) -> str:
        joined = '/'.join([self.display_name, self.selected]).strip('/')
        return f"(Empire: <ansired>{joined}</ansired>) > "

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
            self.agent_options = state.agents[agent_name] # todo rename agent_options

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
    def update_comms(self, listener_name: str) -> None:
        """
        Update the listener for an agent.

        Usage: update_comms <listener_name>
        """
        response = state.update_agent_comms(self.selected, listener_name)

        if 'success' in response.keys():
            print(print_util.color('[*] Updated agent ' + self.selected + ' listener ' + listener_name))
        elif 'error' in response.keys():
            print(print_util.color('[!] Error: ' + response['error']))

    @command
    def killdate(self, kill_date: str) -> None:
        """
        Set an agent's killdate (01/01/2020)

        Usage: killdate <kill_date>
        """
        response = state.update_agent_killdate(self.selected, kill_date)

        if 'success' in response.keys():
            print(print_util.color('[*] Updated agent ' + self.selected + ' killdate to ' + kill_date))
        elif 'error' in response.keys():
            print(print_util.color('[!] Error: ' + response['error']))


interact_menu = InteractMenu()

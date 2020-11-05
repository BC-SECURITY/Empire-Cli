import shlex
import threading
import time

from prompt_toolkit.completion import Completion
from terminaltables import SingleTable

import print_util
from EmpireCliState import state
from Menu import Menu
from utils import register_cli_commands, command


@register_cli_commands
class ShellMenu(Menu):
    def __init__(self):
        super().__init__()
        self.selected_type = ''
        self.display_name = ''

    def autocomplete(self):
        return self._cmd_registry + super().autocomplete()

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()
        try:
            cmd_line = list(map(lambda s: s.lower(), shlex.split(document.current_line)))
            # print(cmd_line)
        except ValueError:
            pass
        else:
            yield from super().get_completions(document, complete_event)

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
                    print(print_util.color(results['results']))
                    status_result = True
            except:
                pass
            time.sleep(1)

    @command
    def use(self, agent_name: str) -> None:
        """
        Use shell

        Usage: shell
        """
        self.update_directory(agent_name)

    def update_directory(self, agent_name: str):
        """
        Update current directory

        Usage:  update_directory <agent_name>
        """
        temp_name = None
        task_id: str = str(state.agent_shell(agent_name, '(Resolve-Path .\).Path')['taskID'])

        # Retrieve directory results and wait for response
        while temp_name is None:
            temp_name = state.get_task_result(agent_name, task_id)['results']
            time.sleep(1)
        self.display_name = temp_name

    def shell(self, agent_name: str, shell_cmd: str):
        """
        Tasks an the specified agent_name to execute a shell command.

        Usage:  <shell_cmd>
        """
        response = state.agent_shell(agent_name, shell_cmd)
        if shell_cmd.split()[0].lower() in ['cd', 'set-location']:
            self.update_directory(agent_name)
        else:
            shell_return = threading.Thread(target=self.tasking_id_returns, args=[self.selected_type, response['taskID']])
            shell_return.start()


shell_menu = ShellMenu()

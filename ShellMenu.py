import shlex
import string
import textwrap
import time

from prompt_toolkit.completion import Completion
from terminaltables import SingleTable

from EmpireCliState import state
from utils import register_cli_commands, command


@register_cli_commands
class ShellMenu(object):
    def __init__(self):
        self.selected_type = ''
        self.display_name = ''

    def autocomplete(self):
        return self._cmd_registry + [
            'help',
            'main',
            'list',
            'interact',
        ]

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()
        try:
            cmd_line = list(map(lambda s: s.lower(), shlex.split(document.current_line)))
            # print(cmd_line)
        except ValueError:
            pass
        else:
            for word in self.autocomplete():
                if word.startswith(word_before_cursor):
                    yield Completion(word, start_position=-len(word_before_cursor), style="underline")

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
        state.agent_shell(agent_name, shell_cmd)
        if shell_cmd.split()[0].lower() in ['cd', 'set-location']:
            self.update_directory(agent_name)

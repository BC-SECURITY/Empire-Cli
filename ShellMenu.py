import shlex
import time

from EmpireCliState import state
from Menu import Menu
from utils import register_cli_commands, command, position_util


@register_cli_commands
class ShellMenu(Menu):
    def __init__(self):
        super().__init__()
        self.selected_type = ''
        self.display_name = ''

    def autocomplete(self):
        return self._cmd_registry + super().autocomplete()

    def get_completions(self, document, complete_event, cmd_line, word_before_cursor):
        if position_util(cmd_line, 1, word_before_cursor):
            yield from super().get_completions(document, complete_event, cmd_line, word_before_cursor)

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


shell_menu = ShellMenu()

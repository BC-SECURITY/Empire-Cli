import time
import threading

from utils import print_util
from EmpireCliState import state
from Menu import Menu
from utils.autocomplete_utils import position_util
from utils.cli_utils import register_cli_commands


@register_cli_commands
class ShellMenu(Menu):
    def __init__(self):
        super().__init__(display_name='', selected='')

    def autocomplete(self):
        return self._cmd_registry + super().autocomplete()

    def get_completions(self, document, complete_event, cmd_line, word_before_cursor):
        if position_util(cmd_line, 1, word_before_cursor):
            yield from super().get_completions(document, complete_event, cmd_line, word_before_cursor)

    def init(self, **kwargs) -> bool:
        if 'selected' not in kwargs:
            return False
        else:
            self.use(kwargs['selected'])
            return True

    def get_prompt(self) -> str:
        return f"<ansiblue>({self.selected})</ansiblue> <ansired>{self.display_name}</ansired> > "

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

    def use(self, agent_name: str) -> None:
        """
        Use shell

        Usage: shell
        """
        self.selected = agent_name
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
            try:
                temp_name = state.get_task_result(agent_name, task_id)['results']
            except:
                pass
            time.sleep(1)
        self.display_name = temp_name
        self.get_prompt()

    def shell(self, agent_name: str, shell_cmd: str):
        """
        Tasks an the specified agent_name to execute a shell command.

        Usage:  <shell_cmd>
        """
        response = state.agent_shell(agent_name, shell_cmd)
        if shell_cmd.split()[0].lower() in ['cd', 'set-location']:
            shell_return = threading.Thread(target=self.update_directory, args=[agent_name])
            shell_return.start()
        else:
            shell_return = threading.Thread(target=self.tasking_id_returns, args=[self.selected, response['taskID']])
            shell_return.start()


shell_menu = ShellMenu()

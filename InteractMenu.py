import shlex
import threading
import time

from prompt_toolkit.completion import Completion
from terminaltables import SingleTable

from EmpireCliState import state
from Menu import Menu
from utils import register_cli_commands, command


@register_cli_commands
class InteractMenu(Menu):
    def __init__(self):
        super().__init__(display_name='', selected='')

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
            if len(cmd_line) > 0 and cmd_line[0] in ['interact']:
                for type in state.agent_types:
                    yield Completion(type, start_position=-len(word_before_cursor))
            else:
                yield from super().get_completions(document, complete_event)

    def tasking_id_returns(self, agent_name, task_id: int):
        """
        Polls and prints tasking data for taskID

        Usage: tasking_id_returns <agent_name> <task_id>
        """
        # todo: there must be a better way to do this with notifications
        # Set previous results to current results to avoid a lot of old data
        status_result = False

        while not status_result:
            try:
                results = state.get_agent_result(agent_name)['results'][0]['AgentResults'][task_id - 1]
                if results['results'] is not None:
                    print('[*] Task ' + str(results['taskID']) + " results:")
                    print(results['results'])
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
        self.selected = agent_name
        self.display_name = self.selected
        if self.selected in state.agent_types:
            for x in range(len(state.agents['agents'])):
                if state.agents['agents'][x]['name'] == self.selected:
                    self.agent_options = state.agents['agents'][x]

    @command
    def shell(self, shell_cmd: str) -> None:
        """
        Tasks an the specified agent to execute a shell command.

        Usage: shell <shell_cmd>
        """
        response = state.agent_shell(self.selected, shell_cmd)
        print('[*] Tasked ' + self.selected + ' to run Task ' + str(response['taskID']))
        agent_return = threading.Thread(target=self.tasking_id_returns, args=[self.selected, response['taskID']])
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
        #todo: the spacing looks off on the table
        agent_list = []
        for key, value in self.agent_options.items():
            if isinstance(value, int):
                value = str(value)
            if value is None:
                value = ''
            temp = [key, value]
            agent_list.append(temp)

        table = SingleTable(agent_list)
        table.title = 'Agent Options'
        table.inner_row_border = True
        print(table.table)


interact_menu = InteractMenu()

import shlex
import string
import textwrap
import threading
import time

from prompt_toolkit.completion import Completion

import table_util
from EmpireCliState import state
from Menu import Menu
from utils import register_cli_commands, command


@register_cli_commands
class UseModuleMenu(Menu):
    def __init__(self):
        super().__init__(display_name='usemodule', selected='')
        self.module_options = {}

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
            if len(cmd_line) > 0 and cmd_line[0] in ['usemodule']:
                for module in state.modules.keys():
                    yield Completion(module, start_position=-len(word_before_cursor))
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
                    if 'Job started:' not in results['results']:
                        print('[*] Task ' + str(results['taskID']) + " results:")
                        print(results['results'])
                        status_result = True
            except:
                pass
            time.sleep(1)

    @command
    def use(self, module: str) -> None:
        """
        Use the selected module

        Usage: use <module>
        """
        if module in state.modules.keys():
            self.selected = module
            self.display_name = 'usemodule/' + self.selected
            self.module_options = state.modules[module]['options']

    @command
    def set(self, key: string, value: string) -> None:
        """
        Set a field for the current module

        Usage: set <key> <value>
        """
        if key in self.module_options:
            self.module_options[key]['Value'] = value

        # todo use python prompt print methods for formatting
        print(f'Set {key} to {value}')

    @command
    def unset(self, key: str) -> None:
        """
        Unset a module option.

        Usage: unset <key>
        """
        if key in self.module_options:
            self.module_options[key]['Value'] = ''

        # todo use python prompt print methods for formatting
        print(f'Unset {key}')

    @command
    def info(self):
        """
        Print the current module options

        Usage: info
        """
        module_list = []
        for key, value in self.module_options.items():
            values = list(map(lambda x: '\n'.join(textwrap.wrap(str(x), width=35)), value.values()))
            values.reverse()
            temp = [key] + values
            module_list.append(temp)

        table_util.print_table(module_list, 'Module Options')

    @command
    def execute(self):
        """
        Execute the selected module

        Usage: start
        """
        # todo validation and error handling
        # Hopefully this will force us to provide more info in api errors ;)
        post_body = {}
        for key, value in self.module_options.items():
            post_body[key] = self.module_options[key]['Value']

        response = state.execute_module(self.selected, post_body)

        print('[*] Tasked ' + self.module_options['Agent']['Value'] + ' to run Task ' + str(response['taskID']))
        agent_return = threading.Thread(target=self.tasking_id_returns, args=[self.module_options['Agent']['Value'], response['taskID']])
        agent_return.start()


use_module_menu = UseModuleMenu()

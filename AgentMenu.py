import string

from terminaltables import SingleTable

from EmpireCliState import state

# This needs to be updated to match how ListenerMenu works.
class AgentMenu(object):
    def __init__(self):
        self.display_name = "agents"

    def autocomplete(self):
        return [
            'agent-struff',
            'list',
            'agentcrap'
        ]

    def execute(self, text: string) -> None:
        if text == 'list':
            agents = state.get_agents()
            agent_list = list(map(lambda x: [x['name'], x['listener'], x['language'], x['username'], trunc(x['process_name'], 10), x['process_id'], x['lastseen_time']], agents['agents']))
            agent_list.insert(0, ['Name', 'Listener', 'Language', 'Username', 'Process', 'PID', 'Last Seen'])
            table = SingleTable(agent_list)
            table.title = 'Agents List'
            table.inner_row_border = True
            print(table.table)
        # print('hi!' + text)


def trunc(value: string = '', limit: int = 1) -> string:
    if value:
        if len(value) > limit:
            return value[:limit - 2] + '..'
        else:
            return value
    return ''

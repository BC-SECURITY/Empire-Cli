import json
from typing import Dict, Optional

import requests
import socketio


class EmpireCliState(object):
    def __init__(self):
        self.host = ''
        self.port = ''
        self.token = ''
        self.sio: Optional[socketio.Client] = None
        self.connected = False
        self.listeners = []
        self.listener_types = []
        self.stagers = []
        self.stager_types = []
        self.modules = []
        self.module_types = []
        self.agents = []
        self.agent_types = []

    def connect(self, host, port, socketport, username, password):
        self.host = host
        self.port = port
        response = requests.post(url=f'{host}:{port}/api/admin/login',
                                 json={'username': username, 'password': password},
                                 verify=False)

        self.token = json.loads(response.content)['token']
        self.connected = True

        self.sio = socketio.Client(ssl_verify=False)
        self.sio.connect(f'{host}:{socketport}?token={self.token}')

        print('Connected to ' + host)

        self.init()
        self.init_handlers()

    def init(self):
        self.listeners = self.get_listeners()
        self.listener_types = self.get_listener_types()
        self.stagers = self.get_stagers()
        self.stager_types = {'types': list(map(lambda x: x['Name'], self.stagers['stagers']))}
        self.modules = self.get_modules()
        self.module_types = {'types': list(map(lambda x: x['Name'], self.modules['modules']))}
        self.agents = self.get_agents()
        self.agent_types = {'types': list(map(lambda x: x['name'], self.agents['agents']))}

    def init_handlers(self):
        if self.sio:
            self.sio.on('listeners/new', lambda data: print(data))

    def disconnect(self):
        self.host = ''
        self.port = ''
        self.token = ''
        self.connected = False

    def get_listeners(self):
        response = requests.get(url=f'{self.host}:{self.port}/api/listeners',
                                verify=False,
                                params={'token': self.token})

        return json.loads(response.content)

    def kill_listener(self, listener_name: str):
        response = requests.delete(url=f'{self.host}:{self.port}/api/listeners/{listener_name}',
                                   verify=False,
                                   params={'token': self.token})

        return json.loads(response.content)

    def get_listener_types(self):
        response = requests.get(url=f'{self.host}:{self.port}/api/listeners/types',
                                verify=False,
                                params={'token': self.token})

        return json.loads(response.content)

    def get_listener_options(self, module: str):
        response = requests.get(url=f'{self.host}:{self.port}/api/listeners/options/{module}',
                                verify=False,
                                params={'token': self.token})

        return json.loads(response.content)

    def create_listener(self, module: str, options: Dict):
        response = requests.post(url=f'{self.host}:{self.port}/api/listeners/{module}',
                                 json=options,
                                 verify=False,
                                 params={'token': self.token})

        return json.loads(response.content)

    def get_stagers(self):
        response = requests.get(url=f'{self.host}:{self.port}/api/stagers',
                                verify=False,
                                params={'token': self.token})

        return json.loads(response.content)

    def create_stager(self, module: str, options: Dict):
        options['StagerName'] = module
        response = requests.post(url=f'{self.host}:{self.port}/api/stagers',
                                 json=options,
                                 verify=False,
                                 params={'token': self.token})

        return json.loads(response.content)

    def get_agents(self):
        response = requests.get(url=f'{self.host}:{self.port}/api/agents',
                                verify=False,
                                params={'token': self.token})

        return json.loads(response.content)

    def get_modules(self):
        response = requests.get(url=f'{self.host}:{self.port}/api/modules',
                                verify=False,
                                params={'token': self.token})

        return json.loads(response.content)

    def kill_agent(self, agent_name: str):
        response = requests.post(url=f'{self.host}:{self.port}/api/agents/{agent_name}/kill',
                                 verify=False,
                                 params={'token': self.token})

        return json.loads(response.content)

    def clear_agent(self, agent_name: str):
        response = requests.post(url=f'{self.host}:{self.port}/api/agents/{agent_name}/clear',
                                 verify=False,
                                 params={'token': self.token})

        return json.loads(response.content)

    def rename_agent(self, agent_name: str, new_agent_name: str):
        response = requests.post(url=f'{self.host}:{self.port}/api/agents/{agent_name}/rename',
                                 json={'newname': new_agent_name},
                                 verify=False,
                                 params={'token': self.token})

        return json.loads(response.content)

    def agent_shell(self, agent_name, shell_cmd: str):
        response = requests.post(url=f'{self.host}:{self.port}/api/agents/{agent_name}/shell',
                                 json={'command': shell_cmd},
                                 verify=False,
                                 params={'token': self.token})

        return json.loads(response.content)

    def scrape_directory(self, agent_name):
        response = requests.post(url=f'{self.host}:{self.port}/api/agents/{agent_name}/directory',
                                 verify=False,
                                 params={'token': self.token})

        return json.loads(response.content)

    def get_directory(self, agent_name):
        response = requests.get(url=f'{self.host}:{self.port}/api/agents/{agent_name}/directory',
                                 verify=False,
                                 params={'token': self.token})

        return json.loads(response.content)

    def get_result(self, agent_name):
        response = requests.get(url=f'{self.host}:{self.port}/api/agents/{agent_name}/results',
                                 verify=False,
                                 params={'token': self.token})

        return json.loads(response.content)

    def get_task_result(self, agent_name, task_id):
        response = requests.get(url=f'{self.host}:{self.port}/api/agents/{agent_name}/task/{task_id}',
                                 verify=False,
                                 params={'token': self.token})

        return json.loads(response.content)

    def get_creds(self):
        response = requests.get(url=f'{self.host}:{self.port}/api/creds',
                                verify=False,
                                params={'token': self.token})

        return json.loads(response.content)

state = EmpireCliState()

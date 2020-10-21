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

        # TODO Seprate sio class? at least for the handlers?
        self.sio.on('listeners/new', lambda data: print(data))

        print('Connected to ' + host)

        self.init()

    def init(self):
        self.listeners = self.get_listeners()
        self.listener_types = self.get_listener_types()

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


state = EmpireCliState()

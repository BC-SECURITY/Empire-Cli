import json
from typing import Dict

import requests
import socketio

# print('connecting')
# sio = socketio.Client()
# sio.connect('http://192.168.0.18:5000?token=b8jtcz3eu65064askr9uwchsr31czftyz5n693df')
#
# @sio.event
# def connect():
#     print('connected')
# #
# #
# @sio.on('listeners/new')
# def on_message(data):
#     print('I received a message!')
#     print(data)


def get_agents():
    response = requests.get(url='https://localhost:1337/api/agents',
                            verify=False,
                            params={'token': 'b8jtcz3eu65064askr9uwchsr31czftyz5n693df'})

    return json.loads(response.content)


def get_listeners():
    response = requests.get(url='https://localhost:1337/api/listeners',
                            verify=False,
                            params={'token': 'b8jtcz3eu65064askr9uwchsr31czftyz5n693df'})

    return json.loads(response.content)


def kill_listener(listener_name: str):
    response = requests.delete(url=f'https://localhost:1337/api/listeners/{listener_name}',
                               verify=False,
                               params={'token': 'b8jtcz3eu65064askr9uwchsr31czftyz5n693df'})

    return json.loads(response.content)


def get_listener_types():
    response = requests.get(url=f'https://localhost:1337/api/listeners/types',
                            verify=False,
                            params={'token': 'b8jtcz3eu65064askr9uwchsr31czftyz5n693df'})

    return json.loads(response.content)


def get_listener_options(module: str):
    response = requests.get(url=f'https://localhost:1337/api/listeners/options/{module}',
                            verify=False,
                            params={'token': 'b8jtcz3eu65064askr9uwchsr31czftyz5n693df'})

    return json.loads(response.content)


def create_listener(module: str, options: Dict):
    response = requests.post(url=f'https://localhost:1337/api/listeners/{module}',
                             json=options,
                             verify=False,
                             params={'token': 'b8jtcz3eu65064askr9uwchsr31czftyz5n693df'})

    return json.loads(response.content)


def get_stagers():
    response = requests.get(url=f'https://localhost:1337/api/stagers',
                            verify=False,
                            params={'token': 'b8jtcz3eu65064askr9uwchsr31czftyz5n693df'})

    return json.loads(response.content)


def create_stager(module: str, options: Dict):
    options['StagerName'] = module
    response = requests.post(url=f'https://localhost:1337/api/stagers',
                             json=options,
                             verify=False,
                             params={'token': 'b8jtcz3eu65064askr9uwchsr31czftyz5n693df'})

    return json.loads(response.content)

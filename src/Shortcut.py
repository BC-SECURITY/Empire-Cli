from typing import List, Optional

from src.utils import print_util


# https://yzhong-cs.medium.com/serialize-and-deserialize-complex-json-in-python-205ecc636caa
class ShortcutParam(object):
    def __init__(self, name: str, dynamic: bool = False, value: Optional[str] = ''):
        self.name = name
        self.dynamic = dynamic
        self.value = value

    @classmethod
    def from_json(cls, data):
        return cls(**data)


class Shortcut(object):
    def __init__(self, name: str, module: str, params: List[ShortcutParam]):
        self.name = name
        self.module = module
        self.params = [] if not params else params

    def get_dynamic_params(self) -> List[ShortcutParam]:
        return list(filter(lambda x: x.dynamic, self.params))

    def get_dynamic_param_names(self) -> List[str]:
        return list(map(lambda x: x.name, self.get_dynamic_params()))

    def get_static_params(self) -> List[ShortcutParam]:
        return list(filter(lambda x: not x.dynamic, self.params))

    def get_static_param_names(self) -> List[str]:
        return list(map(lambda x: x.name, self.get_static_params()))

    def get_param(self, name: str) -> Optional[ShortcutParam]:
        param = None
        for p in self.params:
            if p.name == name:
                param = p
                break

        return param

    def get_usage_string(self) -> str:
        usage = f'{self.name} '
        params = self.get_dynamic_param_names()
        for param in params:
            usage += f'<{param}> '

        return usage

    def get_help_description(self) -> str:
        module = self.module
        default_params = list(map(lambda x: f"{x.name}: {x.value}", self.get_static_params()))
        description = f"Tasks the agent to run module {module}."
        if len(default_params) > 0:
            description += ' Default parameters include:\n'
            description += '\n'.join(default_params)

        return print_util.text_wrap(description)

    @classmethod
    def from_json(cls, data):
        data['params'] = [] if 'params' not in data else list(map(ShortcutParam.from_json, data['params']))
        return cls(**data)

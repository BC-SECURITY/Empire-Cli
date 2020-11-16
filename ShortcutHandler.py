from typing import List, Dict

from EmpireCliConfig import empire_config
from utils import print_util


class ShortcutHandler:
    def __init__(self):
        self.shortcuts = empire_config.yaml.get('shortcuts', {})
        # Todo validate to a schema? Map to an object?

    def get(self, language: str, name: str) -> Dict:
        return self.shortcuts.get(language, {}).get(name)

    def get_as_dict(self, language: str) -> Dict:
        return self.shortcuts.get(language, {})

    def get_names(self, language: str) -> List[str]:
        return list(self.shortcuts.get(language, {}).keys())

    def get_dynamic_params(self, language: str, name: str):
        shortcut = self.get(language, name)
        return list(filter(lambda x: x.get('dynamic'), shortcut.get('params', [])))

    def get_dynamic_param_names(self, language: str, name: str):
        shortcut = self.get(language, name)
        return list(map(lambda x: x['name'], filter(lambda x: x.get('dynamic'), shortcut.get('params', []))))

    def get_static_params(self, language: str, name: str):
        shortcut = self.get(language, name)
        return list(map(lambda x: f"{x['name']}: {x['value']}",
                        filter(lambda x: not x.get('dynamic'), shortcut.get('params', []))))

    def get_usage_string(self, language: str, name: str) -> str:
        usage = f'{name} '
        params = self.get_dynamic_param_names(language, name)
        for param in params:
            usage += f'<{param}> '

        return usage

    def get_help_description(self, language: str, name: str) -> str:
        shortcut = self.get(language, name)
        module = shortcut['module']
        default_params = self.get_static_params(language, name)
        description = f"Tasks the agent to run module {module}."
        if len(default_params) > 0:
            description += ' Default parameters include:\n'
            description += '\n'.join(default_params)

        return print_util.text_wrap(description)


shortcut_handler = ShortcutHandler()

import json
from typing import List, Dict

from src.EmpireCliConfig import empire_config
from src.Shortcut import Shortcut


class ShortcutHandler:
    """
    Handler class to get shortcuts.
    """

    def __init__(self):
        shortcuts_raw = empire_config.yaml.get('shortcuts', {})
        python: Dict[str, Shortcut] = {}
        powershell: Dict[str, Shortcut] = {}
        for key, value in shortcuts_raw['python'].items():
            value['name'] = key
            python[key] = Shortcut.from_json(json.loads(json.dumps(value)))
        for key, value in shortcuts_raw['powershell'].items():
            value['name'] = key
            powershell[key] = Shortcut.from_json(json.loads(json.dumps(value)))
        self.shortcuts: Dict[str, Dict[str, Shortcut]] = {'python': python, 'powershell': powershell}

    def get(self, language: str, name: str) -> Shortcut:
        return self.shortcuts.get(language, {}).get(name)

    def get_names(self, language: str) -> List[str]:
        return list(self.shortcuts.get(language, {}).keys())


shortcut_handler = ShortcutHandler()

from prompt_toolkit.completion import Completion

from utils.autocomplete_utils import filtered_search_list


class Menu(object):
    def __init__(self, display_name: str = '', selected: str = ''):
        self.display_name = display_name
        self.selected = selected

    def autocomplete(self):
        return [
            'help',
            'main',
            'back',
            'interact',
            'listeners',
            'uselistener',
            'usestager',
            'plugins',
            'useplugin',
            'agents',
            'usemodule',
            'credentials',
            'exit',
        ]

    def get_completions(self, document, complete_event, cmd_line, word_before_cursor):
        word_before_cursor = document.get_word_before_cursor()
        for word in filtered_search_list(word_before_cursor, self.autocomplete()):
            if word.startswith(word_before_cursor):
                yield Completion(word, start_position=-len(word_before_cursor))

    def init(self, **kwargs) -> bool:
        return True

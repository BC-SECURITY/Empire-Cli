from prompt_toolkit.completion import Completion


class Menu(object):
    def __init__(self, display_name: str = '', selected: str = ''):
        self.display_name = display_name
        self.selected = selected

    def autocomplete(self):
        return ['help', 'main', 'interact']

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()
        for word in self.autocomplete():
            if word.startswith(word_before_cursor):
                yield Completion(word, start_position=-len(word_before_cursor))

    def init(self):
        pass

from prompt_toolkit.completion import Completion

from utils.autocomplete_utils import filtered_search_list


class Menu(object):
    def __init__(self, display_name: str = '', selected: str = ''):
        # The display name for the menu. This is used by the default get_prompt method.
        self.display_name = display_name
        # The selected item. Applicable for Menus such UseStager or UseListener.
        self.selected = selected

    def autocomplete(self):
        """
        The default list of autocomplete commands aka 'the globals'
        A menu should return its own list in addition to these globals.
        :return: list[str]
        """
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
        """
        The default completion method. A menu should implement its own get_completion method
        for autocompleting its own commands and then use this as a fallback for autocompleting the globals.
        """
        word_before_cursor = document.get_word_before_cursor()
        for word in filtered_search_list(word_before_cursor, self.autocomplete()):
            if word.startswith(word_before_cursor):
                yield Completion(word, start_position=-len(word_before_cursor))

    def init(self, **kwargs) -> bool:
        """
        When a user changes menus, the init method will be called. Returning True means that
        changing menus succeeded. Any initialization that needs to happen should happen here before returning.
        For example: Checking to see that the requested module is available, setting it to self.selected, and then
        printing out its options.
        :param kwargs: A menu can implement with any specific kwargs it needs
        :return: bool
        """
        return True

    def get_prompt(self) -> str:
        """
        This is the (HTML-wrapped) string that will be used for the prompt. If it doesn't need to be customized,
        this will display a combination of the menu's display name and the selected item.
        :return:
        """
        joined = '/'.join([self.display_name, self.selected]).strip('/')
        return f"(Empire: <ansiblue>{joined}</ansiblue>) > "

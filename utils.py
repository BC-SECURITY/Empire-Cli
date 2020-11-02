import functools
from typing import List


def command(func):
    func._command = True

    @functools.wraps(func)
    def wrap(*args, **kwargs):
        return func(*args, **kwargs)
    return wrap


def register_cli_commands(cls):
    cls._cmd_registry = []
    for methodname in dir(cls):
        method = getattr(cls, methodname)
        if hasattr(method, '_command'):
            cls._cmd_registry.append(methodname)
    return cls


def filtered_search_list(prefix: str, keys) -> List[str]:
    return list(filter(lambda x: x.lower().startswith(prefix.lower()), keys))


def position_util(cmd_line: List[str], word_position: int, word_before_cursor: str) -> bool:
    """
    Util method for autocompletion conditions. Makes autocomplete work well.

    :param cmd_line:
    :param word_position:
    :param word_before_cursor:
    :return:
    """
    # Special case for no characters typed yet (we send in [''] as cmd_line which fucks with the logic)
    if word_position == 1 and len(cmd_line) == 1 and cmd_line[0] == '':
        return True
    # Don't keep completing after the word position
    # Don't complete if we just hit space after the word position
    # Don't complete on the previous word position until there is a space
    return len(cmd_line) < word_position + 1\
        and not (len(cmd_line) == word_position and word_before_cursor == '')\
        and not (len(cmd_line) == word_position - 1 and word_before_cursor != '')

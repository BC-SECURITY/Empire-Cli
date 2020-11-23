from typing import List


def filtered_search_list(search: str, keys) -> List[str]:
    """
    Filters the search list by a search string
    :param search: the string prefix
    :param keys: the list of strings to search
    :return: filtered list
    """
    return list(filter(lambda x: (search.lower()) in x.lower(), keys))


def position_util(cmd_line: List[str], word_position: int, word_before_cursor: str) -> bool:
    """
    Util method for autocompletion conditions. Makes autocomplete work well.

    :param cmd_line: the list of command line words
    :param word_position: the position of the word we are attempting to autocomplete
    :param word_before_cursor: word_before_cursor parsed from the document
    :return: True if we should try to autocomplete this word.
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

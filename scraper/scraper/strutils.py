def is_alpha_char(letter: str) -> bool:
    return len(letter) == 1 and letter.isalpha() and letter.isascii()


def substring_ignore_case(substring: str, fullstring: str) -> bool:
    return substring.casefold() in fullstring.casefold()

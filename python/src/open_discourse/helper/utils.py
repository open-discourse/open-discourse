import pyparsing as pp


def get_term_from_path(path: str) -> int | None:
    """
    Extracts the electoral term number from the folder path.
    """
    electoral_term_parser = "electoral_term_pp" + pp.Word(pp.nums, exact=2)
    term_number = electoral_term_parser.search_string(path, max_matches=1)
    term_number = term_number[0][1] if term_number else None

    if term_number is not None:
        term_number = int(term_number)

    return term_number

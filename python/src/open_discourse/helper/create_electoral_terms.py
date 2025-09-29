from datetime import datetime, timedelta


def create_electoral_terms():
    """
    Create dict of electoral terms with start_date,
    end_date (start_date of the following electoral_term minus one day,
    number of sessions per electoral term.

    Returns:
        dict: electoral_terms
    """
    electoral_terms = {
        1: {"start_date": "1949-09-07", "number_of_sessions": 282},
        2: {"start_date": "1953-10-06", "number_of_sessions": 227},
        3: {"start_date": "1957-10-15", "number_of_sessions": 168},
        4: {"start_date": "1961-10-17", "number_of_sessions": 198},
        5: {"start_date": "1965-10-19", "number_of_sessions": 247},
        6: {"start_date": "1969-10-20", "number_of_sessions": 199},
        7: {"start_date": "1972-12-13", "number_of_sessions": 259},
        8: {"start_date": "1976-12-14", "number_of_sessions": 230},
        9: {"start_date": "1980-11-04", "number_of_sessions": 142},
        10: {"start_date": "1983-03-29", "number_of_sessions": 256},
        11: {"start_date": "1987-02-18", "number_of_sessions": 236},
        12: {"start_date": "1990-12-20", "number_of_sessions": 243},
        13: {"start_date": "1994-11-10", "number_of_sessions": 248},
        14: {"start_date": "1998-10-26", "number_of_sessions": 253},
        15: {"start_date": "2002-10-17", "number_of_sessions": 187},
        16: {"start_date": "2005-10-18", "number_of_sessions": 233},
        17: {"start_date": "2009-10-27", "number_of_sessions": 253},
        18: {"start_date": "2013-10-22", "number_of_sessions": 245},
        19: {"start_date": "2017-10-24", "number_of_sessions": 239},
        20: {"start_date": "2021-10-26", "number_of_sessions": 214},
        21: {"start_date": "2025-03-25", "end_date": None, "number_of_sessions": None},
    }

    # Set end_date for every electoral_term but the current
    for i in range(max(electoral_terms) - 1, 0, -1):
        # subtract one day from start_date of the following electoral_term
        tmp_date = datetime.strptime(
            electoral_terms[i + 1]["start_date"], "%Y-%m-%d"
        ) - timedelta(days=1)
        # reconvert to str-format
        electoral_terms[i]["end_date"] = tmp_date.strftime("%Y-%m-%d")

    return electoral_terms

from datetime import datetime

import pandas as pd

import open_discourse.definitions.path_definitions as path_definitions

# output directory
ELECTORAL_TERMS = path_definitions.ELECTORAL_TERMS
ELECTORAL_TERMS.mkdir(parents=True, exist_ok=True)

electoral_terms = [
    {"start_date": "1949-09-07", "end_date": "1953-10-05"},
    {"start_date": "1953-10-06", "end_date": "1957-10-14"},
    {"start_date": "1957-10-15", "end_date": "1961-10-16"},
    {"start_date": "1961-10-17", "end_date": "1965-10-18"},
    {"start_date": "1965-10-19", "end_date": "1969-10-19"},
    {"start_date": "1969-10-20", "end_date": "1972-12-12"},
    {"start_date": "1972-12-13", "end_date": "1976-12-13"},
    {"start_date": "1976-12-14", "end_date": "1980-11-03"},
    {"start_date": "1980-11-04", "end_date": "1983-03-28"},
    {"start_date": "1983-03-29", "end_date": "1987-02-17"},
    {"start_date": "1987-02-18", "end_date": "1990-12-19"},
    {"start_date": "1990-12-20", "end_date": "1994-11-09"},
    {"start_date": "1994-11-10", "end_date": "1998-10-25"},
    {"start_date": "1998-10-26", "end_date": "2002-10-16"},
    {"start_date": "2002-10-17", "end_date": "2005-10-17"},
    {"start_date": "2005-10-18", "end_date": "2009-10-26"},
    {"start_date": "2009-10-27", "end_date": "2013-10-21"},
    {"start_date": "2013-10-22", "end_date": "2017-10-23"},
    {"start_date": "2017-10-24", "end_date": "2021-10-26"},
    {"start_date": "2021-10-27", "end_date": "2025-10-29"},
]


def string_to_seconds(date_string, ref_date=datetime(year=1970, month=1, day=1)):
    date = datetime.strptime(date_string, "%Y-%m-%d")
    return (date - ref_date).total_seconds()


# convert dates to total seconds and add 1-based id to each term
electoral_terms = [
    {key: string_to_seconds(date_string) for key, date_string in term.items()}
    | {"id": idx + 1}
    for idx, term in enumerate(electoral_terms)
]

save_path = ELECTORAL_TERMS / "electoral_terms.csv"
pd.DataFrame(electoral_terms).to_csv(save_path, index=False)

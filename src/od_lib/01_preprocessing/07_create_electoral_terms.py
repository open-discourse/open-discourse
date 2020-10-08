import od_lib.definitions.path_definitions as path_definitions
import pandas as pd
import datetime
import os

# output directory
ELECTORAL_TERMS = path_definitions.ELECTORAL_TERMS
save_path = os.path.join(ELECTORAL_TERMS, "electoral_terms.csv")

if not os.path.exists(ELECTORAL_TERMS):
    os.makedirs(ELECTORAL_TERMS)

electoral_terms = [
    {
        "id": 1,
        "start_date": (
            datetime.datetime.strptime("1949-09-07", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
        "end_date": (
            datetime.datetime.strptime("1953-10-05", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
    },
    {
        "id": 2,
        "start_date": (
            datetime.datetime.strptime("1953-10-06", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
        "end_date": (
            datetime.datetime.strptime("1957-10-14", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
    },
    {
        "id": 3,
        "start_date": (
            datetime.datetime.strptime("1957-10-15", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
        "end_date": (
            datetime.datetime.strptime("1961-10-16", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
    },
    {
        "id": 4,
        "start_date": (
            datetime.datetime.strptime("1961-10-17", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
        "end_date": (
            datetime.datetime.strptime("1965-10-18", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
    },
    {
        "id": 5,
        "start_date": (
            datetime.datetime.strptime("1965-10-19", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
        "end_date": (
            datetime.datetime.strptime("1969-10-19", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
    },
    {
        "id": 6,
        "start_date": (
            datetime.datetime.strptime("1969-10-20", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
        "end_date": (
            datetime.datetime.strptime("1972-12-12", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
    },
    {
        "id": 7,
        "start_date": (
            datetime.datetime.strptime("1972-12-13", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
        "end_date": (
            datetime.datetime.strptime("1976-12-13", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
    },
    {
        "id": 8,
        "start_date": (
            datetime.datetime.strptime("1976-12-14", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
        "end_date": (
            datetime.datetime.strptime("1980-11-03", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
    },
    {
        "id": 9,
        "start_date": (
            datetime.datetime.strptime("1980-11-04", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
        "end_date": (
            datetime.datetime.strptime("1983-03-28", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
    },
    {
        "id": 10,
        "start_date": (
            datetime.datetime.strptime("1983-03-29", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
        "end_date": (
            datetime.datetime.strptime("1987-02-17", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
    },
    {
        "id": 11,
        "start_date": (
            datetime.datetime.strptime("1987-02-18", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
        "end_date": (
            datetime.datetime.strptime("1990-12-19", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
    },
    {
        "id": 12,
        "start_date": (
            datetime.datetime.strptime("1990-12-20", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
        "end_date": (
            datetime.datetime.strptime("1994-11-09", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
    },
    {
        "id": 13,
        "start_date": (
            datetime.datetime.strptime("1994-11-10", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
        "end_date": (
            datetime.datetime.strptime("1998-10-25", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
    },
    {
        "id": 14,
        "start_date": (
            datetime.datetime.strptime("1998-10-26", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
        "end_date": (
            datetime.datetime.strptime("2002-10-16", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
    },
    {
        "id": 15,
        "start_date": (
            datetime.datetime.strptime("2002-10-17", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
        "end_date": (
            datetime.datetime.strptime("2005-10-17", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
    },
    {
        "id": 16,
        "start_date": (
            datetime.datetime.strptime("2005-10-18", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
        "end_date": (
            datetime.datetime.strptime("2009-10-26", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
    },
    {
        "id": 17,
        "start_date": (
            datetime.datetime.strptime("2009-10-27", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
        "end_date": (
            datetime.datetime.strptime("2013-10-21", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
    },
    {
        "id": 18,
        "start_date": (
            datetime.datetime.strptime("2013-10-22", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
        "end_date": (
            datetime.datetime.strptime("2017-10-23", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
    },
    {
        "id": 19,
        "start_date": (
            datetime.datetime.strptime("2017-10-24", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
        "end_date": (
            datetime.datetime.strptime("2021-10-24", "%Y-%m-%d")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds(),
    },
]

pd.DataFrame(electoral_terms).to_csv(save_path, index=False)

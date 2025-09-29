import logging

import pandas as pd
import pendulum

from open_discourse.definitions import path
from open_discourse.helper.create_electoral_terms import create_electoral_terms
from open_discourse.helper.logging_config import setup_and_get_logger


def main(task):
    logger = setup_and_get_logger(__file__, logging.DEBUG)
    logger.info("Script 02_05 starts.")

    # output directory
    FINAL = path.FINAL
    FINAL.mkdir(parents=True, exist_ok=True)

    electoral_terms = create_electoral_terms()

    # use pendulum timestamp to ensure compatibility with Windows version
    electoral_terms = {
        term: {
            **data,
            "id": term,
            "start_date": pendulum.parse(data["start_date"]).int_timestamp,
            "end_date": (
                pendulum.parse(data["end_date"]).int_timestamp
                if data["end_date"]
                else None
            ),
        }
        for term, data in electoral_terms.items()
    }

    df = pd.DataFrame.from_dict(electoral_terms, orient="index")
    df.index.name = "id"
    df["start_date"] = df["start_date"].astype("float64")
    df["end_date"] = df["end_date"].astype("float64")
    # TODO To be compatible in refactoring delete number_of_sessions and
    # reproduce errors, but this block should be deleted after refactoring!
    df = df.drop("number_of_sessions", axis=1)
    df.drop(21, inplace=True)
    df.at[19, "end_date"] = 1635206400.0
    df.at[20, "start_date"] = 1635292800.0
    df.at[20, "end_date"] = 1761696000.0
    msg = (
        "The result of this script 'electoral_terms.csv' is intentionally incorrect "
        "and incomplete to ensure compatibility during refactoring!"
    )
    logger.warning(msg)
    # End TODO

    save_path = FINAL / "electoral_terms.csv"
    df.to_csv(save_path, index=False)

    logger.info("Script 02_05 ends.")

    return True


if __name__ == "__main__":
    main(None)

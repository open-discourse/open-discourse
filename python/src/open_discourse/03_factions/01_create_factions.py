"""
Script to extract and create a basic factions dataset from politicians' data.

This script is part of the Open Discourse pipeline and performs the following tasks:
1. Loads politicians' data from a pickle file
2. Extracts unique faction names where institution_type is "Fraktion/Gruppe"
3. Adds additional predefined factions from constants
4. Saves the resulting factions DataFrame to a pickle file

The output of this script serves as input for the subsequent faction processing step 
(02_add_abbreviations_and_ids.py) which adds abbreviations and unique IDs.
"""

import numpy as np
import pandas as pd

# Project-specific imports
import open_discourse.definitions.path_definitions as path_definitions
from open_discourse.helper_functions.logging_config import configure_logger
from open_discourse.helper_functions.constants import ADDITIONAL_FACTIONS

# Configure a logger for this script
logger = configure_logger("process_factions")

def extract_unique_factions(mps: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts unique faction names from the given politicians DataFrame and appends additional predefined factions.

    This function filters the input DataFrame to include only rows where 'institution_type' is "Fraktion/Gruppe",
    then extracts unique faction names from the 'institution_name' column. It also appends any additional factions
    specified in the ADDITIONAL_FACTIONS constant.

    Args:
        mps (pd.DataFrame): A DataFrame containing politicians' data. It must include the columns
            'institution_type' and 'institution_name'.

    Returns:
        pd.DataFrame: A DataFrame with a single column "faction_name" that contains the unique faction names
        extracted from the input DataFrame, including the additional factions.
    """
    # Cut dataframe down to two columns
    required_cols = {"institution_type", "institution_name"}
    if not required_cols.issubset(mps.columns):
        missing = required_cols - set(mps.columns)
        logger.error(f"Missing required columns in DataFrame: {missing}")
        raise ValueError(f"Missing required columns in DataFrame: {missing}")

    # Filter rows where institution_type is "Fraktion/Gruppe"
    factions_series = mps.loc[mps["institution_type"] == "Fraktion/Gruppe", "institution_name"]

    # Extract unique faction names
    unique_factions = np.unique(factions_series)

    # Append additional predefined factions
    all_factions = np.append(unique_factions, ADDITIONAL_FACTIONS)

    # Convert the result to a DataFrame, will eventually be saved to file
    return pd.DataFrame(all_factions, columns=["faction_name"])

def main() -> None:
    """
    Main function that loads the mps DataFrame, extracts unique factions,
    and saves them to 'factions.pkl' in the designated output directory.
    """
    # Define input/output paths
    POLITICIANS_STAGE_01 = path_definitions.POLITICIANS_STAGE_01
    FACTIONS_STAGE_01 = path_definitions.FACTIONS_STAGE_01
    FACTIONS_STAGE_01.mkdir(parents=True, exist_ok=True)

    # Load the politicians' data from a pickle file for further processing
    mps_path = POLITICIANS_STAGE_01 / "mps.pkl"
    try:
        mps = pd.read_pickle(mps_path)
        logger.info(f"Loaded 'mps.pkl' from {mps_path}")
    except Exception as e:
        logger.error(f"Failed to load {mps_path}: {e}")
        return

    # Extract the unique names of factions/groups from the politicians' data via extract_unique_factions()
    try:
        unique_factions_df = extract_unique_factions(mps)
        logger.info("Extracted unique factions successfully.")
    except ValueError as ve:
        logger.error(f"Data validation error: {ve}")
        return
    except Exception as e:
        logger.error(f"Unexpected error during faction extraction: {e}")
        return

    # Save the unique factions factions DataFrame, final log after success
    output_file = FACTIONS_STAGE_01 / "factions.pkl"
    try:
        unique_factions_df.to_pickle(output_file)
        logger.info(f"Unique factions saved to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save {output_file}: {e}")
        return

    logger.info("Script completed: 03_01_process_factions.py done.")

if __name__ == "__main__":
    main()

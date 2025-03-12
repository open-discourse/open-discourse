#!/usr/bin/env python
"""
Script to enhance the faction dataset with abbreviations and unique IDs.

This script is part of the Open Discourse pipeline and performs the following tasks:
1. Loads the basic factions data created by 01_create_factions.py
2. Adds standardized abbreviations to each faction using predefined mappings
3. Assigns unique numerical IDs to each faction based on their abbreviations
4. Saves the fully processed factions data to the final data directory

The resulting dataset is used throughout the Open Discourse project to standardize
faction references and provide consistent identifiers for parliamentary groups.
"""

import numpy as np
import pandas as pd

# Project-specific imports
import open_discourse.definitions.path_definitions as path_definitions
from open_discourse.helper_functions.constants import FACTION_ABBREVIATIONS
from open_discourse.helper_functions.logging_config import configure_logger
from open_discourse.helper_functions.io_utils import load_pickle, save_pickle

# Configure a logger for this script
logger = configure_logger("process_factions")

def _get_abbreviation(faction_name: str) -> str:
    """
    Get the standardized abbreviation for a faction name.
    
    Args:
        faction_name (str): The full faction name to look up in the FACTION_ABBREVIATIONS dictionary
        
    Returns:
        str: The standardized abbreviation if the faction name is found in FACTION_ABBREVIATIONS,
             otherwise returns the original faction_name as a fallback
    """
    if faction_name in FACTION_ABBREVIATIONS:
        return FACTION_ABBREVIATIONS[faction_name]
    else:
        # Return the faction name itself as a fallback
        return faction_name

def add_abbreviations_to_factions(factions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds abbreviations to faction names based on predefined mapping.
    
    Args:
        factions_df (pd.DataFrame): DataFrame containing faction names in the 'faction_name' column
        
    Returns:
        pd.DataFrame: DataFrame with an additional 'abbreviation' column at index 0. The original
                      data is preserved, and for faction names without a standard abbreviation, 
                      the original faction name is used as the abbreviation.
    
    Raises:
        KeyError: If 'faction_name' column is missing from the input DataFrame
    """
    logger.info("Adding abbreviations to factions")
    
    # Create a copy to avoid modifying the input DataFrame
    result_df = factions_df.copy()
    
    # Insert new column at the beginning
    result_df.insert(0, "abbreviation", "")
    
    # Track missing factions
    missing_factions = []
    
    # Helper function to track missing factions while getting abbreviation
    def track_and_get_abbreviation(faction_name):
        abbreviation = _get_abbreviation(faction_name)
        if abbreviation == faction_name and faction_name not in FACTION_ABBREVIATIONS:
            missing_factions.append(faction_name)
        return abbreviation
    
    # Apply the function to each faction name
    result_df["abbreviation"] = result_df["faction_name"].apply(track_and_get_abbreviation)
    
    # Log any missing factions as warnings
    if missing_factions:
        unique_missing = set(missing_factions)
        logger.warning(f"Found {len(unique_missing)} faction names without abbreviation mappings: {unique_missing}")
        logger.warning("Using original names as abbreviations for these factions")
    
    return result_df

def assign_ids_to_factions(factions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Assigns unique IDs to factions based on their abbreviations.
    
    Args:
        factions_df (pd.DataFrame): DataFrame containing faction abbreviations in the 'abbreviation' column
        
    Returns:
        pd.DataFrame: DataFrame with an additional 'id' column at index 0
    
    Raises:
        KeyError: If 'abbreviation' column is missing from the input DataFrame
    """
    logger.info("Assigning IDs to factions based on abbreviations")
    
    # Create a copy to avoid modifying the input DataFrame
    result_df = factions_df.copy()
    
    # Get unique abbreviations and generate sequential IDs
    unique_abbreviations = np.unique(result_df["abbreviation"])
    faction_ids = list(range(len(unique_abbreviations)))
    
    # Insert new ID column at the beginning with default value -1
    result_df.insert(0, "id", -1)
    
    # Assign IDs based on abbreviations
    for abbrev, id_value in zip(unique_abbreviations, faction_ids):
        result_df.loc[result_df["abbreviation"] == abbrev, "id"] = id_value
    
    logger.info(f"Assigned {len(unique_abbreviations)} unique IDs to factions")
    return result_df

def main() -> None:
    """
    Main function that loads factions data, adds abbreviations and IDs,
    and saves the result to the final directory.
    
    Returns:
        None: This function doesn't return any values but exits early on errors
    """
    # Define input/output paths
    FACTIONS_STAGE_01 = path_definitions.FACTIONS_STAGE_01
    DATA_FINAL = path_definitions.DATA_FINAL
    DATA_FINAL.mkdir(parents=True, exist_ok=True)
    
    # Load the factions data
    input_file = FACTIONS_STAGE_01 / "factions.pkl"
    factions = load_pickle(input_file, logger)
    if factions is None:
        return  # Early return if loading failed
    
    # Process the data: add abbreviations and IDs
    try:
        # Add abbreviations
        factions_with_abbrevs = add_abbreviations_to_factions(factions)
        
        # Add IDs based on abbreviations
        final_factions = assign_ids_to_factions(factions_with_abbrevs)
        
        logger.info("Successfully processed factions data")
    except TypeError as e:
        logger.error(f"Type error during faction processing: {e}")
        return
    except ValueError as e:
        logger.error(f"Value error during faction processing: {e}")
        return
    except KeyError as e:
        logger.error(f"Key error during faction processing (missing column?): {e}")
        return
    except Exception as e:
        logger.error(f"Unexpected error processing factions data: {e}")
        return
    
    # Save the processed data
    output_file = DATA_FINAL / "factions.pkl"
    if not save_pickle(final_factions, output_file, logger):
        return  # Early return if saving failed
    
    logger.info("Script completed: 03_02_add_abbreviations_and_ids.py done.")
    print("Script 03_02 done.")

if __name__ == "__main__":
    main()

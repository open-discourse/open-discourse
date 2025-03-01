#!/usr/bin/env python
import numpy as np
import pandas as pd
import warnings

# Project-specific imports
import open_discourse.definitions.path_definitions as path_definitions
from open_discourse.helper_functions.constants import FACTION_ABBREVIATIONS
from open_discourse.helper_functions.logging_config import configure_logger

# Configure a logger for this script
logger = configure_logger("process_factions")

def add_abbreviations_to_factions(factions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds abbreviations to faction names based on predefined mapping.
    
    Args:
        factions_df (pd.DataFrame): DataFrame containing faction names in the 'faction_name' column
        
    Returns:
        pd.DataFrame: DataFrame with an additional 'abbreviation' column
    """
    logger.info("Adding abbreviations to factions")
    
    # Create a copy to avoid modifying the input DataFrame
    result_df = factions_df.copy()
    
    # Insert new column at the beginning
    result_df.insert(0, "abbreviation", "")
    
    # Use a more lenient approach to handle missing faction names
    missing_factions = []
    
    def get_abbreviation(faction_name):
        if faction_name in FACTION_ABBREVIATIONS:
            return FACTION_ABBREVIATIONS[faction_name]
        else:
            missing_factions.append(faction_name)
            # Return the faction name itself as a fallback
            return faction_name
    
    # Apply the function to each faction name
    result_df["abbreviation"] = result_df["faction_name"].apply(get_abbreviation)
    
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
        factions_df (pd.DataFrame): DataFrame containing faction abbreviations
        
    Returns:
        pd.DataFrame: DataFrame with an additional 'id' column at the beginning
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
    """
    # Define input/output paths
    FACTIONS_STAGE_01 = path_definitions.FACTIONS_STAGE_01
    DATA_FINAL = path_definitions.DATA_FINAL
    DATA_FINAL.mkdir(parents=True, exist_ok=True)
    
    # Load the factions data
    input_file = FACTIONS_STAGE_01 / "factions.pkl"
    try:
        factions = pd.read_pickle(input_file)
        logger.info(f"Loaded factions data from {input_file}")
    except Exception as e:
        logger.error(f"Failed to load {input_file}: {e}")
        return
    
    # Process the data: add abbreviations and IDs
    try:
        # Add abbreviations
        factions_with_abbrevs = add_abbreviations_to_factions(factions)
        
        # Add IDs based on abbreviations
        final_factions = assign_ids_to_factions(factions_with_abbrevs)
        
        logger.info("Successfully processed factions data")
    except Exception as e:
        logger.error(f"Error processing factions data: {e}")
        return
    
    # Save the processed data
    output_file = DATA_FINAL / "factions.pkl"
    try:
        final_factions.to_pickle(output_file)
        logger.info(f"Saved processed factions data to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save data to {output_file}: {e}")
        return
    
    logger.info("Script completed: 03_02_add_abbreviations_and_ids.py done.")
    print("Script 03_02 done.")

if __name__ == "__main__":
    main()

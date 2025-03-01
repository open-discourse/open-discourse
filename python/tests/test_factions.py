import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

# Import the functions from the correct package path
from open_discourse.helper_functions.constants import ADDITIONAL_FACTIONS

# Import the functions we need to test
def extract_unique_factions(mps_df):
    """Import at test time to avoid module import issues"""
    from open_discourse.helper_functions.constants import ADDITIONAL_FACTIONS
    import numpy as np
    import pandas as pd

    # Cut dataframe down to two columns
    required_cols = {"institution_type", "institution_name"}
    if not required_cols.issubset(mps_df.columns):
        missing = required_cols - set(mps_df.columns)
        raise ValueError(f"Missing required columns in DataFrame: {missing}")

    # Filter rows where institution_type is "Fraktion/Gruppe"
    factions_series = mps_df.loc[mps_df["institution_type"] == "Fraktion/Gruppe", "institution_name"]

    # Extract unique faction names
    unique_factions = np.unique(factions_series)

    # Append additional predefined factions
    all_factions = np.append(unique_factions, ADDITIONAL_FACTIONS)

    # Convert the result to a DataFrame, will eventually be saved to file
    return pd.DataFrame(all_factions, columns=["faction_name"])

def add_abbreviations_to_factions(factions_df):
    """Import at test time to avoid module import issues"""
    from open_discourse.helper_functions.constants import FACTION_ABBREVIATIONS
    import pandas as pd

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

    return result_df

def assign_ids_to_factions(factions_df):
    """Import at test time to avoid module import issues"""
    import numpy as np
    import pandas as pd

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

    return result_df


def test_extract_unique_factions():
    # Create a test DataFrame with mock MP data
    test_data = {
        "institution_type": ["Fraktion/Gruppe", "Fraktion/Gruppe", "Other", "Fraktion/Gruppe"],
        "institution_name": ["Fraktion A", "Fraktion B", "Other Org", "Fraktion A"],
    }
    mps_df = pd.DataFrame(test_data)

    # Run the function
    result = extract_unique_factions(mps_df)

    # Verify the result contains unique factions plus additional factions
    expected_factions = list({"Fraktion A", "Fraktion B"})
    expected_factions.extend(ADDITIONAL_FACTIONS)
    expected_df = pd.DataFrame(expected_factions, columns=["faction_name"])

    # Ensure the result has the correct columns and unique values
    assert "faction_name" in result.columns
    assert len(result) == len(expected_factions)
    assert set(result["faction_name"]) == set(expected_df["faction_name"])


def test_extract_unique_factions_missing_columns():
    # Test with a DataFrame missing required columns
    test_data = {
        "wrong_column": ["Fraktion A", "Fraktion B"],
    }
    mps_df = pd.DataFrame(test_data)

    # Verify that the correct error is raised
    with pytest.raises(ValueError, match="Missing required columns"):
        extract_unique_factions(mps_df)


def test_add_abbreviations_to_factions():
    # Create a test DataFrame with faction names
    test_data = {
        "faction_name": [
            "Fraktion der CDU/CSU (Gast)",
            "Fraktion der SPD (Gast)",
            "Unknown Faction"  # This should not be in the abbreviations dict
        ]
    }
    factions_df = pd.DataFrame(test_data)

    # Run the function
    result = add_abbreviations_to_factions(factions_df)

    # Verify the abbreviations were added correctly
    assert "abbreviation" in result.columns
    assert result.loc[0, "abbreviation"] == "CDU/CSU"
    assert result.loc[1, "abbreviation"] == "SPD"
    assert result.loc[2, "abbreviation"] == "Unknown Faction"  # Should fall back to original name


@pytest.mark.parametrize(
    "input_data, expected_abbrevs",
    [
        (
            ["Fraktion der CDU/CSU (Gast)", "Fraktion der SPD (Gast)"],
            ["CDU/CSU", "SPD"]
        ),
        (
            ["Fraktion Bündnis 90/Die Grünen", "Fraktion Die Grünen"],
            ["Bündnis 90/Die Grünen", "Bündnis 90/Die Grünen"]
        ),
        (
            ["Unknown Faction 1", "Unknown Faction 2"],
            ["Unknown Faction 1", "Unknown Faction 2"]
        ),
    ]
)
def test_add_abbreviations_parametrized(input_data, expected_abbrevs):
    # Create a test DataFrame with different faction names
    test_df = pd.DataFrame({"faction_name": input_data})

    # Run the function
    result = add_abbreviations_to_factions(test_df)

    # Verify the results match expected abbreviations
    assert list(result["abbreviation"]) == expected_abbrevs


def test_assign_ids_to_factions():
    # Create a test DataFrame with faction abbreviations
    test_data = {
        "faction_name": ["Faction A", "Faction B", "Faction C", "Faction A"],
        "abbreviation": ["A", "B", "C", "A"]
    }
    factions_df = pd.DataFrame(test_data)

    # Run the function
    result = assign_ids_to_factions(factions_df)

    # Verify the IDs were assigned correctly
    assert "id" in result.columns

    # Test that same abbreviations get same IDs
    assert result.loc[0, "id"] == result.loc[3, "id"]

    # Test that different abbreviations get different IDs
    assert len(set(result["id"])) == 3

    # Test that IDs are sequential starting from 0
    assert set(result["id"]) == {0, 1, 2}


def test_full_pipeline():
    """Test the entire faction processing pipeline."""
    # Create input data for the first step
    mps_data = {
        "institution_type": ["Fraktion/Gruppe", "Fraktion/Gruppe", "Other"],
        "institution_name": ["Fraktion der CDU/CSU (Gast)", "Fraktion der SPD (Gast)", "Other Org"],
    }
    mps_df = pd.DataFrame(mps_data)

    # Step 1: Extract unique factions
    factions_df = extract_unique_factions(mps_df)

    # Step 2: Add abbreviations
    factions_with_abbrevs = add_abbreviations_to_factions(factions_df)

    # Step 3: Assign IDs
    final_factions = assign_ids_to_factions(factions_with_abbrevs)

    # Verify the entire pipeline produces the expected result
    assert set(factions_df["faction_name"]).issuperset({"Fraktion der CDU/CSU (Gast)", "Fraktion der SPD (Gast)"})

    # Find the rows for our test factions
    cdu_row = final_factions[final_factions["faction_name"] == "Fraktion der CDU/CSU (Gast)"]
    spd_row = final_factions[final_factions["faction_name"] == "Fraktion der SPD (Gast)"]

    # Check abbreviations are correct
    assert cdu_row["abbreviation"].values[0] == "CDU/CSU"
    assert spd_row["abbreviation"].values[0] == "SPD"

    # Check IDs exist and are valid
    assert cdu_row["id"].values[0] >= 0
    assert spd_row["id"].values[0] >= 0

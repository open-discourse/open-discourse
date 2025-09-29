import pytest

from open_discourse.steps.preprocessing.extract_mps_from_mp_base_data import (
    is_valid_date,
)

# Definiere Testfälle als Liste von Tupeln
test_cases = [
    ("12.04.1949", True),  # Valid
    ("15.05.60", False),  # Invalid
    ("29.02.1961", False),  # Invalid
    ("7.3.1970", True),  # Valid
    ("1871-12-23", False),  # Invalid
]


@pytest.mark.parametrize("testdate, expected_result", test_cases)
def test_is_valid_date(testdate, expected_result):
    result = is_valid_date(testdate)

    assert result == expected_result

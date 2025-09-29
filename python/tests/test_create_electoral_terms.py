import pytest

from open_discourse.helper.create_electoral_terms import create_electoral_terms


@pytest.mark.parametrize(
    "term, expected",
    [
        (
            12,
            {
                "start_date": "1990-12-20",
                "end_date": "1994-11-09",
                "number_of_sessions": 243,
            },
        ),
        (
            20,
            {
                "start_date": "2021-10-26",
                "end_date": "2025-03-24",
                "number_of_sessions": 214,
            },
        ),
    ],
)
def test_create_electoral_terms(term, expected):
    result = create_electoral_terms()
    assert result[term]["start_date"] == expected["start_date"]
    assert result[term]["end_date"] == expected["end_date"]
    assert result[term]["number_of_sessions"] == expected["number_of_sessions"]
    # assert result[12]["start_date"] == "1990-12-20"
    # assert result[12]["end_date"] == "1994-11-09"
    # assert result[12]["number_of_sessions"] == 243


def test_create_electoral_terms_error():
    # Access invalid electoral term
    result = create_electoral_terms()
    with pytest.raises(KeyError):
        assert result[0]["start_date"] == "1990-12-20"
    with pytest.raises(KeyError):
        assert result["12"]["start_date"] == "1990-12-20"

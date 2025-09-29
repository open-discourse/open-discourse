import pytest

import open_discourse.steps


@pytest.mark.parametrize(
    "task_fnc, expected_number_actions",
    [
        ("task_01_download", 3),
        ("task_02_preprocessing", 5),
        ("task_03_factions", 2),
        ("task_04_politicians", 3),
        ("task_05_speech_content", 3),
        ("task_06_electoral_term_20", 1),
        ("task_07_contributions", 3),
        ("task_08_upload", 2),
    ],
)
def test_import_steps(task_fnc: str, expected_number_actions: int):
    """Test that all steps can be imported without errors."""
    task_fnc = getattr(open_discourse.steps, task_fnc)
    assert task_fnc()
    assert task_fnc.__doc__
    assert task_fnc.__name__
    assert task_fnc.__name__.startswith("task_")
    assert len(list(task_fnc())) == expected_number_actions

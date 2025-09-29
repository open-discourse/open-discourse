from collections import namedtuple
from pathlib import Path
from types import GeneratorType
from unittest.mock import patch

import pytest

from open_discourse.helper.session_file_iterator import (
    session_file_iterator,
    validate_term_session,
)

# Definition Named Tuple for test cases, don't name it Testcase!!!
CaseDataforTest = namedtuple("CaseDataforTest", ["input", "expected", "exception"])

# ======================================================================================
# test cases for test_validate_term_session()
# ======================================================================================
test_cases = []
test_cases.append(CaseDataforTest((5, 5, "single"), expected=[5], exception=None))
test_cases.append(
    CaseDataforTest((0, 4, "single"), expected=None, exception=ValueError)
)
test_cases.append(CaseDataforTest((5, 6, "single"), expected=[5], exception=None))
test_cases.append(
    CaseDataforTest((5, 4, "single"), expected=None, exception=ValueError)
)
test_cases.append(
    CaseDataforTest((5, -1, "single"), expected=None, exception=ValueError)
)
test_cases.append(
    CaseDataforTest(("5", 4, "single"), expected=None, exception=TypeError)
)
test_cases.append(
    CaseDataforTest((5, "5", "single"), expected=None, exception=TypeError)
)

test_cases.append(
    CaseDataforTest(((4, 5), 5, "double"), expected=[4, 5], exception=None)
)
test_cases.append(
    CaseDataforTest(((5, 4), 5, "double"), expected=None, exception=ValueError)
)
test_cases.append(
    CaseDataforTest(((3, 6), 5, "double"), expected=None, exception=ValueError)
)
test_cases.append(
    CaseDataforTest(((-1, 6), 7, "double"), expected=None, exception=ValueError)
)
test_cases.append(
    CaseDataforTest(((3.0, 6), 7, "double"), expected=None, exception=TypeError)
)


@pytest.mark.parametrize("case", test_cases)
def test_validate_term_session(case: namedtuple):
    if case.exception:
        with pytest.raises(case.exception):
            validate_term_session(*case.input)
    else:
        assert case.expected == validate_term_session(*case.input)


# ========================================
# test cases for session_file_iterator
# ========================================
test_cases = []
test_cases.append(
    CaseDataforTest(
        {"source_dir": "RAW_XML", "term": 4, "session": 19},
        expected=["04019"],
        exception=None,
    )
)
test_cases.append(
    CaseDataforTest(
        {"source_dir": "RAW_XML", "term": 4, "session": None},
        expected=["04019", "04034", "04056"],
        exception=None,
    )
)
test_cases.append(
    CaseDataforTest(
        {"source_dir": "RAW_XML", "term": None, "session": None},
        expected=[
            "04019",
            "04034",
            "04056",
            "09019",
            "09034",
            "09056",
            "15019",
            "15034",
            "15056",
        ],
        exception=None,
    )
)
test_cases.append(
    CaseDataforTest(
        {"source_dir": "RAW_TXT", "term": 4, "session": 19},
        expected=["04019"],
        exception=None,
    )
)
test_cases.append(
    CaseDataforTest(
        {"source_dir": "RAW_TXT", "term": 4, "session": None},
        expected=["04019", "04034", "04056"],
        exception=None,
    )
)
test_cases.append(
    CaseDataforTest(
        {"source_dir": "RAW_TXT", "term": None, "session": None},
        expected=[
            "04019",
            "04034",
            "04056",
            "09019",
            "09034",
            "09056",
            "15019",
            "15034",
            "15056",
        ],
        exception=None,
    )
)

test_cases.append(
    CaseDataforTest(
        {"source_dir": "SPEECH_CONTENT_STAGE_02", "term": 4, "session": 19},
        expected=["04019"],
        exception=None,
    )
)
test_cases.append(
    CaseDataforTest(
        {"source_dir": "SPEECH_CONTENT_STAGE_02", "term": 4, "session": None},
        expected=["04019", "04034", "04056"],
        exception=None,
    )
)
test_cases.append(
    CaseDataforTest(
        {"source_dir": "SPEECH_CONTENT_STAGE_02", "term": None, "session": None},
        expected=[
            "04019",
            "04034",
            "04056",
            "09019",
            "09034",
            "09056",
            "15019",
            "15034",
            "15056",
        ],
        exception=None,
    )
)


@pytest.fixture(scope="module")
def module_tmp_path(tmp_path_factory):
    return tmp_path_factory.mktemp("session_iterator_test")


@pytest.fixture(scope="module")
def dynamic_patch_paths(module_tmp_path):
    """
    Patch some of the paths from path to enable tests in module_tmp_path
    based directories, e.g. RAW_XML.
    Only paths, that are needed for this test are patched!
    module_tmp_path with tmp_path_factory is ued, so that the test files are created
    only once for al test cases.

    Args:
        module_tmp_path (): pytest tmp_path_factory

    Returns: dict of patched pathes

    """

    # DATA
    mocked_DATA = module_tmp_path / "data"
    mocked_DATA_RAW = mocked_DATA / "01_raw"
    mocked_DATA_CACHE = mocked_DATA / "02_cached"
    # mocked_DATA_FINAL = mocked_DATA / "03_final"

    # RAW
    mocked_RAW_XML = mocked_DATA_RAW / "xml"
    mocked_RAW_TXT = mocked_DATA_RAW / "txt"

    # SPEECH CONTENT
    mocked_SPEECH_CONTENT_STAGE_02 = mocked_DATA_CACHE / "speech_content" / "stage_02"

    # dict
    mocked_paths = {
        # "DATA_RAW": mocked_DATA_RAW,
        "RAW_XML": mocked_RAW_XML,
        "RAW_TXT": mocked_RAW_TXT,
        "SPEECH_CONTENT_STAGE_02": mocked_SPEECH_CONTENT_STAGE_02,
    }

    with patch.multiple("open_discourse.helper.session_file_iterator", **mocked_paths):
        yield mocked_paths


@pytest.fixture(scope="module")
def prepare_valid_test_files(dynamic_patch_paths):
    """
    Prepare test files once for all tests of session_file_iterator
    """

    for elem in ["RAW_XML", "RAW_TXT", "SPEECH_CONTENT_STAGE_02"]:
        test_dir = dynamic_patch_paths[elem]
        if elem == "RAW_XML":
            suffix = ".xml"
        elif elem == "RAW_TXT":
            suffix = ".txt"
        elif elem == "SPEECH_CONTENT_STAGE_02":
            suffix = ".pkl"
        else:
            suffix = ""

        # 4 testfiles in 3 directories, one is invalid filename format

        term_list = sorted([4, 9, 15])
        session_list = sorted([19, 34, 56])

        for t in term_list:
            # create directories based on tmp_path
            create_dir = Path(test_dir, f"electoral_term_pp{t:02}.zip")
            create_dir.mkdir(parents=True, exist_ok=True)
            if elem == "RAW_XML" or elem == "SPEECH_CONTENT_STAGE_02":
                # invalid file
                sample_file = create_dir / f"x47P13{suffix}"
                sample_file.write_text("<content>Test</content>")
                for s in session_list:
                    sample_file = create_dir / f"{t:02}{s:03}{suffix}"
                    sample_file.write_text("<content>Test</content>")
            elif elem == "RAW_TXT":
                for s in session_list:
                    # create sub directory
                    create_dir = Path(
                        test_dir, f"electoral_term_pp{t:02}.zip", f"{t:02}{s:03}"
                    )
                    create_dir.mkdir(parents=True, exist_ok=True)
                    sample_file = create_dir / "session_content.txt"
                    sample_file.write_text("<content>Test</content>")


@pytest.mark.parametrize("case", test_cases)
def test_session_file_iterator(
    case: namedtuple, dynamic_patch_paths, prepare_valid_test_files
):
    test_dir = dynamic_patch_paths[case.input["source_dir"]]
    assert "pytest" in str(test_dir)

    if case.exception:
        with pytest.raises(case.exception):
            next(session_file_iterator(*case.input))
    else:
        result = session_file_iterator(
            test_dir, case.input["term"], case.input["session"]
        )
        assert isinstance(result, GeneratorType)
        result_list = list(result)
        assert len(result_list) == len(case.expected)
        result_short_list = []
        for r in result_list:
            # special handling of text, due to session_content as filename and
            # additional sub directory
            print("test_dir:", test_dir.parts)
            if set(("01_raw", "txt")).issubset(test_dir.parts):
                assert r.stem == "session_content"
                result_short_list.append(r.parent.stem)
            else:
                result_short_list.append(r.stem)
        assert sorted(result_short_list) == sorted(case.expected)


test_cases = []
test_cases.append(
    CaseDataforTest(
        {"source_dir": "anydir"},
        expected=None,
        exception=ValueError,
    )
)
test_cases.append(
    CaseDataforTest(
        {"source_dir": "SPEECH_CONTENT", "term": 4, "session": 19},
        expected=None,
        exception=ValueError,
    )
)


@pytest.mark.parametrize("case", test_cases)
def test_session_file_iterator_exception(case: namedtuple):
    if case.exception:
        with pytest.raises(case.exception):
            next(session_file_iterator(*case.input))

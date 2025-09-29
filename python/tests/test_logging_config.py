import logging
import os
from collections import namedtuple
from pathlib import Path
from unittest.mock import patch

import pytest

from open_discourse.helper.logging_config import setup_and_get_logger

# Definition Named Tuple for test cases, don't name it Testcase!!!
CaseDataforTest = namedtuple("CaseDataforTest", ["input", "expected", "exception"])


@pytest.fixture
def patch_log_path(tmp_path):
    """
    Patch LOG_DIR-path to tmp_path.

    Args:
        tmp_path (): pytest tmp_path

    Returns: patched LOG_DIR-path
    """

    # LOGS DIR
    mocked_LOGS_DIR = tmp_path / "logs"

    with patch("open_discourse.definitions.path.LOGS_DIR", mocked_LOGS_DIR):
        yield {"LOGS_DIR": mocked_LOGS_DIR}


# ========================================
# test cases for setup_and_get_logger
# ========================================
test_cases = []

# TC0: log line written
test_cases.append(
    CaseDataforTest(
        {
            "file_name": "test_logging",
            "log_level": logging.INFO,
            "msg_level": logging.INFO,
            "msg_text": "This is a specific log text",
        },
        expected=(logging.INFO, "This is a specific log text\n"),
        exception=None,
    )
)
# TC1: log line written into log-filename with dot
test_cases.append(
    CaseDataforTest(
        {
            "file_name": "test_log.ging.whatever",
            "log_level": logging.WARNING,
            "msg_level": logging.ERROR,
            "msg_text": "This is a specific log text",
        },
        expected=(logging.ERROR, "This is a specific log text\n"),
        exception=None,
    )
)
# TC2: log line NOT written due to lower msg_level
test_cases.append(
    CaseDataforTest(
        {
            "file_name": "test_logging",
            "log_level": logging.INFO,
            "msg_level": logging.DEBUG,
            "msg_text": "This is a specific log text",
        },
        expected=None,
        exception=None,
    )
)
# TC3: bad log_level
test_cases.append(
    CaseDataforTest(
        {
            "file_name": "test_logging",
            "log_level": 12,
            "msg_level": logging.DEBUG,
            "msg_text": "This is a specific log text",
        },
        expected=(logging.DEBUG, "This is a specific log text\n"),
        exception=None,
    )
)
# TC4: bad log_level
test_cases.append(
    CaseDataforTest(
        {
            "file_name": "test_logging",
            "log_level": "logging.WARNING",  # this is a string!
            "msg_level": logging.DEBUG,
            "msg_text": "This is a specific log text",
        },
        expected=(logging.DEBUG, "This is a specific log text\n"),
        exception=None,
    )
)
# TC5: bad type msg_text
test_cases.append(
    CaseDataforTest(
        {
            "file_name": "test_logging",
            "log_level": 12,
            "msg_level": logging.DEBUG,
            "msg_text": 153,
        },
        expected=(logging.DEBUG, "153\n"),
        exception=None,
    )
)
# TC6: log line written to file but not on console
test_cases.append(
    CaseDataforTest(
        {
            "file_name": "test_logging",
            "log_level": logging.DEBUG,
            "msg_level": logging.DEBUG,
            "msg_text": "This is a specific log text",
        },
        expected=(logging.DEBUG, "This is a specific log text\n"),
        exception=None,
    )
)


@pytest.mark.parametrize("case", test_cases)
def test_setup_and_get_logger(case: namedtuple, patch_log_path, capfd):
    log_filename = case.input["file_name"]
    log_file_path = Path(
        patch_log_path["LOGS_DIR"], str(Path(log_filename).stem + ".log")
    )

    # config logger with log_level from case.input
    logger = setup_and_get_logger(
        log_file=log_filename, log_level=case.input["log_level"]
    )

    # Test 1: exact two handlers
    assert len(logger.handlers) == 2, (
        "Logger should have exact 2 Handler(file & console)"
    )

    # Test 2: log file created?
    assert os.path.exists(log_file_path)

    log_config = {
        logging.DEBUG: ("DEBUG", logger.debug),
        logging.INFO: ("INFO", logger.info),
        logging.WARNING: ("WARNING", logger.warning),
        logging.ERROR: ("ERROR", logger.error),
        logging.CRITICAL: ("CRITICAL", logger.critical),
    }

    # write log line with msg_level and msg_text from case.input
    log_config[case.input["msg_level"]][1](case.input["msg_text"])

    # Test3: check logfile output
    # log line written as expected?
    with open(log_file_path, "r") as log_file:
        log_content = log_file.read()
        if case.expected is None:
            assert len(log_content) == 0
        else:
            assert (
                "ROOT" not in log_content
            )  # The original root handler should not be used
            # check for correct log_level
            assert log_content.endswith(
                log_config[case.expected[0]][0] + " " + case.expected[1]
            )
        # else:
        #     assert case.expected[1] == log_content

    # Test 5: check console output
    captured = (capfd.readouterr()).out
    if case.expected is None:
        assert len(captured) == 0
    else:
        if case.expected[0] == logging.DEBUG:
            assert len(captured) == 0
        else:
            assert log_config[case.expected[0]][0] + " " + case.expected[1] in captured


test_cases = []
# TC0: wrong file_name type
test_cases.append(
    CaseDataforTest(
        {
            "file_name": logging,
            "log_level": logging.INFO,
            "msg_level": logging.INFO,
            "msg_text": "This is a specific log text",
        },
        expected=(logging.INFO, "This is a specific log text"),
        exception=ValueError,
    )
)
# TC1: file_name too short
test_cases.append(
    CaseDataforTest(
        {
            "file_name": "lg",
            "log_level": logging.INFO,
            "msg_level": logging.INFO,
            "msg_text": "This is a specific log text",
        },
        expected=(logging.INFO, "This is a specific log text"),
        exception=ValueError,
    )
)


@pytest.mark.parametrize("case", test_cases)
def test_setup_and_get_logger_invalid_call(case: namedtuple, patch_log_path):
    if case.exception:
        with pytest.raises(case.exception):
            logger = setup_and_get_logger(
                log_file=case.input["file_name"], log_level=case.input["log_level"]
            )
            logger.info("This is a specific invalid log text")
    else:
        assert False

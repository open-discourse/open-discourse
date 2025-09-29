import logging
from pathlib import Path
from typing import Generator

from tqdm import tqdm

from open_discourse.definitions.path import (
    CONTRIBUTIONS_EXTENDED_STAGE_01,
    CONTRIBUTIONS_EXTENDED_STAGE_02,
    CONTRIBUTIONS_EXTENDED_STAGE_03,
    CONTRIBUTIONS_EXTENDED_STAGE_04,
    RAW_TXT,
    RAW_XML,
    SPEECH_CONTENT_STAGE_01,
    SPEECH_CONTENT_STAGE_02,
    SPEECH_CONTENT_STAGE_03,
    SPEECH_CONTENT_STAGE_04,
)
from open_discourse.helper.create_electoral_terms import create_electoral_terms
from open_discourse.helper.utils import get_term_from_path


def validate_term_session(
    param: int | tuple[int, int], max_value: int, param_name: str
) -> list[int]:
    """Check for valid term session.

    Conditions:
    type(param) == int and 0 < param <= max_value
    type(param) == tuple(int,int) and 0 < param[0] <= param[1] <= max_value

    Return range(int1,int2) of param with 0 < int1 <= int2 <= max_value

    Args:
        param (int | tuple[int,int]):   parameter to be checked
        max_value (int):                max_value for param
        param_name (str):               name of param (only used for error msg!)

    Returns: List of valid integers, either a single value or all integers in a range.

    """
    if param is None:
        msg = f"Invalid arg: param {param_name} is None."
        raise ValueError(msg)

    if not isinstance(max_value, int):
        msg = "Invalid type: max_value must be of type int."
        raise TypeError(msg)

    if max_value < 1:
        msg = f"Invalid arg: max_value {max_value} less than 1."
        raise ValueError(msg)

    if not isinstance(param, (int, tuple)):
        raise TypeError(f"Invalid type: {param_name} has type {type(param)}.")

    if isinstance(param, int):
        if not (1 <= param <= max_value):
            msg = f"Invalid arg: {param_name} {param} outside valid range."
            raise ValueError(msg)
        return [param]

    elif isinstance(param, tuple):
        if len(param) != 2:
            msg = f"Invalid arg: {param_name} {param} needs exactly two arguments."
            raise ValueError(msg)

        if not all(isinstance(x, int) for x in param):
            msg = f"Invalid type: All elements in {param_name} should be integers."
            raise TypeError(msg)

        if any(x < 1 or x > max_value for x in param) or param[0] > param[1]:
            msg = (
                f"Invalid arg: {param_name} {param} "
                f"contains values outside valid range."
            )
            raise ValueError(msg)

        return list(range(param[0], param[1] + 1))


def _get_glob(file_pattern: str, term: int):
    if file_pattern == "*.xml":
        glob_pattern = f"electoral_term_pp{term:02}.zip/{file_pattern}"
    elif file_pattern == "session_content.txt":
        glob_pattern = f"electoral_term_pp{term:02}.zip/*/{file_pattern}"
    else:
        glob_pattern = f"electoral_term_pp{term:02}.zip/{file_pattern}"
    return glob_pattern


def session_file_iterator(
    source_dir: Path,
    term: int | tuple[int, int] | None = None,
    session: int | tuple[int, int] | None = None,
) -> Generator[Path, None, None]:
    """
    Iterate through every subfolder of source_dir, e.g. RAW_XML from electoral term 01
    to the highest completed electoral term and return input_file_path.
    Call can be limited to one term or one session by additional args.
    Raises NotImplementedError resp. ValueError when args are not consistent or valid

    Args:
        source_dir (Path):  Path to input directory
        term (int or tuple, optional):         electoral term
        session (int or tuple, optional):      session number in electoral term

    Returns:
        Generator[Path, None, None]: input_file_path form Generator

    """
    file_pattern = {
        RAW_XML: "*.xml",
        RAW_TXT: "session_content.txt",
        SPEECH_CONTENT_STAGE_01: "*.pkl",
        SPEECH_CONTENT_STAGE_02: "*.pkl",
        SPEECH_CONTENT_STAGE_03: "*.pkl",
        SPEECH_CONTENT_STAGE_04: "*.pkl",
        CONTRIBUTIONS_EXTENDED_STAGE_01: "*.pkl",
        CONTRIBUTIONS_EXTENDED_STAGE_02: "*.pkl",
        CONTRIBUTIONS_EXTENDED_STAGE_03: "*.pkl",
        CONTRIBUTIONS_EXTENDED_STAGE_04: "*.pkl",
    }

    if source_dir not in file_pattern:
        raise ValueError(f"Value for {source_dir} currently not supported.")

    assert source_dir.exists(), f"Input directory {source_dir} should exist"

    file_pattern = file_pattern[source_dir]

    # Don't process sub_directories outside scope of this function,
    # that is term 1 to the highest term in SESSIONS_PER_TERM or term in args
    electoral_terms = create_electoral_terms()
    max_term = max(electoral_terms)
    if term is None:
        term_list = list(range(1, max_term + 1))
    else:
        term_list = validate_term_session(term, max_term, "term")

    if session is not None:
        if term is None or len(term_list) != 1:
            msg = (
                f"Invalid arg: exact one term must be set when session {session} is set"
            )
            raise ValueError(msg)
        else:
            term = term_list[0]
            max_session = electoral_terms[term]["number_of_sessions"]
            session_list = validate_term_session(session, max_session, "session")

    # search for file_pattern
    tqdm_bar = None
    for term_number in term_list:
        total_per_term = (
            electoral_terms[term_number]["number_of_sessions"]
            if not session
            else len(session_list)
        )
        # tqdm bar
        if tqdm_bar is not None:
            tqdm_bar.close()

        tqdm_bar = tqdm(
            total=total_per_term,
            desc=f"Parsing term {term_number:>2}...,",
            position=0,
        )

        glob_pattern = _get_glob(file_pattern=file_pattern, term=term_number)

        file_list = sorted(source_dir.glob(glob_pattern), key=lambda x: x.name)
        for input_path in file_list:
            if not input_path.is_file():
                continue

            # session_content.txt-files are in a deeper directory
            if file_pattern == "session_content.txt":
                check_term = int(input_path.parent.name[:2])
                check_session = int(input_path.parent.name[2:])
                check_dir = input_path.parent.parent
            else:
                try:
                    check_term = int(input_path.stem[:2])
                    check_session = int(input_path.stem[2:])
                    check_dir = input_path.parent
                except ValueError:
                    logging.warning(
                        f"Invalid file: {input_path} should not exist in directoy!"
                    )
                    continue

            # Check for relevant session
            if session is not None:
                if check_session not in session_list:
                    continue

            parent = input_path.parent
            # are there any sub_directories?
            if any(child.is_dir() for child in input_path.parent.iterdir()):
                logging.warning(f"Path {parent} should not contain sub_dirs!")

            # check consistency in dir-name electoral_term
            term_in_path = get_term_from_path(str(check_dir))
            if term_in_path != check_term:
                raise ValueError(f"inconsitent {input_path} {check_dir}")

            tqdm_bar.update(1)
            yield input_path

    if tqdm_bar is not None:
        tqdm_bar.close()  # Schließt den letzten Fortschrittsbalken

    return

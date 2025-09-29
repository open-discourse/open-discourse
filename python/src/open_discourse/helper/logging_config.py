import logging
import sys
from logging import FileHandler
from pathlib import Path

from open_discourse.definitions import path


def setup_and_get_logger(
    log_file: str, log_level: int = logging.DEBUG
) -> logging.Logger:
    """
    Setup for Root-Logger; can be used globally.
    Prepare logging to console and file.
    Logging to console only for log_level logging.INFO and more severe.
    Only standard log levels without logging.NOTSET are supported.

    Args:
        log_file (str)  : name of log_file, 3 chars minimum required
        log_level (int) : logging level, e.g. logging.DEBUG (default value)

    Returns:
        logger (logging.Logger):
    """
    # check args
    if not isinstance(log_file, str) or len(log_file) < 3:
        raise ValueError("arg 'log_file' should be a string of 3 chars minimum!")
    # only standard log levels are supported
    if not isinstance(log_level, int) or log_level not in (
        logging.DEBUG,
        logging.INFO,
        logging.WARNING,
        logging.ERROR,
        logging.CRITICAL,
    ):
        log_level = logging.DEBUG

    # default value for root logger
    logging.basicConfig(level=logging.NOTSET)

    # get and config root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # remove all existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # define format
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    # file handler
    logs_dir = path.LOGS_DIR
    logs_dir.mkdir(parents=False, exist_ok=True)  # create logs directory if necessary
    log_file = logs_dir / f"{Path(log_file).stem}.log"

    file_handler = FileHandler(log_file, mode="w", encoding="utf-8")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(max(log_level, logging.INFO))  # No DEBUG-Logs on console
    console_handler.setFormatter(formatter)

    # Add handler
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

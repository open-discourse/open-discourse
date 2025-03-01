# logging_config.py
import logging
import os

def configure_logger(name: str = __name__) -> logging.Logger:
    """
    Configures and returns a logger with both console and file handlers.

    Uses an environment variable 'FACTIONS_LOG_FILE' to determine the log file name.
    Falls back to 'process_factions.log' if not set.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Clear existing handlers in case configure_logger is called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    # Decide the log file name based on environment variable or default
    log_file = os.getenv("FACTIONS_LOG_FILE", "process_factions.log")

    # Format for log messages
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Console handler (INFO+)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # File handler (DEBUG+)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

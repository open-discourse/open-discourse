"""
Utility functions for file I/O operations with proper error handling.

This module provides standardized functions for common I/O operations like
loading and saving data from/to various file formats, with comprehensive
error handling and logging.
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Optional, Any, Union


def load_pickle(file_path: Path, logger: logging.Logger) -> Optional[Any]:
    """
    Safely load a pickle file with comprehensive error handling.
    
    Args:
        file_path (Path): Path to the pickle file to be loaded
        logger (logging.Logger): Logger instance for reporting success or errors
        
    Returns:
        Optional[Any]: The loaded data object if successful, None if loading failed
        
    Raises:
        No exceptions are raised as they are caught and logged internally
    """
    try:
        data = pd.read_pickle(file_path)
        logger.info(f"Loaded data from {file_path}")
        return data
    except FileNotFoundError as e:
        logger.error(f"File not found at {file_path}: {e}")
    except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
        logger.error(f"Data parsing error for {file_path}: {e}")
    except PermissionError as e:
        logger.error(f"Permission denied accessing {file_path}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error loading {file_path}: {e}")
    return None


def save_pickle(data: Any, file_path: Path, logger: logging.Logger) -> bool:
    """
    Safely save data to a pickle file with comprehensive error handling.
    
    Args:
        data (Any): The data object to save (typically a pandas DataFrame or Series)
        file_path (Path): Path where to save the pickle file
        logger (logging.Logger): Logger instance for reporting success or errors
        
    Returns:
        bool: True if saving succeeded, False if any error occurred
        
    Raises:
        No exceptions are raised as they are caught and logged internally
        
    Note:
        The data object must support the to_pickle() method (like pandas objects)
    """
    try:
        data.to_pickle(file_path)
        logger.info(f"Data saved to {file_path}")
        return True
    except PermissionError as e:
        logger.error(f"Permission denied when saving to {file_path}: {e}")
    except OSError as e:
        logger.error(f"OS error when saving to {file_path}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error saving to {file_path}: {e}")
    return False
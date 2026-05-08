"""Configuration loader module for the application.

This module provides functionality to load and parse YAML configuration files.
"""

import logging
from typing import Any, Dict

import yaml

logger = logging.getLogger(__name__)


def load_config(file_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration variables from a YAML file.

    Args:
        file_path: The path to the configuration YAML file. Defaults to "config.yaml".

    Returns:
        A dictionary containing the parsed configuration settings.

    Raises:
        RuntimeError: If there is an issue reading or parsing the configuration file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file_handle:
            return yaml.safe_load(file_handle)
    except Exception as exception:
        logger.error(f"🚨 Config Error: {exception}")
        raise RuntimeError(f"Config Error: {exception}") from exception

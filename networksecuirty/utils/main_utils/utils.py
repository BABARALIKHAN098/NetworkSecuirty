import yaml
from networksecuirty.exception.exception import NetworkSecurityException
from networksecuirty.logging.logger import logging
import os,sys


def read_yaml_file(file_path: str) -> dict:
    """
    Reads a YAML file and returns its contents as a dictionary.
    """
    try:
        with open(file_path, "r") as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e


# Fixed: moved to module level (it was indented inside read_yaml_file)
def write_yaml_file(file_path: str, content: object, replace: bool = False) -> None:
    try:
        # Fixed: only delete the file when replace=True
        if replace and os.path.exists(file_path):
            os.remove(file_path)
        # Fixed: skip makedirs when the path has no folder
        if os.path.dirname(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as yaml_file:
            yaml.dump(content, yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
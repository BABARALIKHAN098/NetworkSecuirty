import os,sys
import json
import numpy as np
import pickle
from networksecuirty.exception.exception import NetworkSecurityException
from networksecuirty.logging.logger import logging

try:
    import yaml
except ImportError:
    yaml = None




def read_yaml_file(file_path: str) -> dict:
    """
    Reads a YAML file and returns its contents as a dictionary.
    """
    try:
        with open(file_path, "r") as yaml_file:
            if yaml is not None:
                return yaml.safe_load(yaml_file)
            result = {}
            current_list = None
            for line in yaml_file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.endswith(":"):
                    key = line[:-1]
                    result[key] = []
                    current_list = result[key]
                elif line.startswith("- ") and current_list is not None:
                    value = line[2:]
                    if ":" in value:
                        key, item = value.split(":", 1)
                        current_list.append({key.strip(): item.strip()})
                    else:
                        current_list.append(value)
            return result
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
            if yaml is not None:
                yaml.dump(content, yaml_file)
            else:
                json.dump(content, yaml_file, indent=2)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e


def save_numpy_array_data(file_path:str,array:np.array):
    """save numpy array data to file file: str location file to wsave array:np.array data to save`"""
    try:
        dir_path=os.path.dirname(file_path)
        os.makedirs(dir_path,exist_ok=True)
        with open(file_path,'wb') as file_obj:
            np.save(file_obj,array)

    except Exception as e:
        raise NetworkSecurityException(e,sys) from e


def save_object(file_path:str,obj:object)->None:
    """save object data to file file: str location file to save obj:object data to save"""
    try:
        logging.info(" Entered the save _object method of Main_utils class")

        os.makedirs(os.path.dirname(file_path),exist_ok=True)

        with open(file_path,'wb') as file_obj:
            pickle.dump(obj,file_obj)
            
        
        logging.info("Exited the save-object method of the Main_utils class")

    except Exception as e:
        raise NetworkSecurityException(e,sys) from e
    
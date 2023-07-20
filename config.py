"""
Loads the configuration file
"""
import json
import os


def load_config():
    with open("config.json") as config_file:
        config = json.load(config_file)
    if "path" not in config.keys():
        current_directory = os.getcwd()
        config["path"] = current_directory
    return config


# Load the configuration file when the module is imported
config = load_config()

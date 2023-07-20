from typing import Dict, List, Union
import json
from singleton_meta import SingletonMeta


class ConnectionLibrary(metaclass=SingletonMeta):
    """
    Singleton class for managing a connection library.
    """

    _loaded = False

    def __init__(self):
        """Initializes the ConnectionLibrary object.

        Reads the configuration file and loads the connection library if it has not been loaded before.

        Attributes:
            connection_library (dict): A dictionary containing the configuration data of the connection library.

        Raises:
            FileNotFoundError: If the configuration file 'hardware_modules/connection_library.json' does not exist.
            JSONDecodeError: If the configuration file is not in valid JSON format.
        """
        if not ConnectionLibrary._loaded:
            with open("hardware_modules/connection_library.json") as config_file:
                config = json.load(config_file)
                self.connection_library = config
            ConnectionLibrary._loaded = True

    def check_port_exists(self, port):
        """
        Checks if a port exists in the connection library.

        Args:
            port (str): The name of the port to check.

        Returns:
            bool: True if the port exists, False otherwise.
        """
        return port in self.connection_library.keys()

    def add_connection(self, connection_name, connection_list):
        """
        Adds a connection to the connection library.

        Args:
            connection_name (str): The name of the connection.
            connection_list (dict): Dictionary containing port names as keys and their types as values.

        Raises:
            ValueError: If the port name is not a string or if the port type is not an int or string,
                or if the port type is a string that doesn't exist in the connection library,
                or if the port width is less than or equal to 0.
        """
        for port, type in connection_list.items():
            if not isinstance(port, str):
                raise ValueError(
                    f"{connection_name} must be made out of ports with names of type string."
                )
            if not isinstance(type, int) and not isinstance(type, str):
                raise ValueError(
                    f"{connection_name} must be made out of ports with types int or string."
                )
            if isinstance(type, str):
                if type not in self.connection_library.keys():
                    raise ValueError(
                        f"Port {port} of type {type} within {connection_name} must exist within the connection library."
                    )
            if isinstance(type, int):
                if type <= 0:
                    raise ValueError(
                        f"Port {port} of width {type} within {connection_name} must have a width greater than 0."
                    )
        self.connection_library[connection_name] = connection_list

    def to_json(self, filename):
        """
        Converts the connection library to JSON and saves it to a file.

        Args:
            filename (str): The name of the JSON file to save the connection library.

        Raises:
            IOError: If there is an error writing the JSON file.
        """
        with open("generated_files/" + filename + ".json", "w") as outfile:
            json.dump(self.connection_library, outfile, indent=4)

from typing import Dict, List, Union
import json
from singleton_meta import SingletonMeta


class ConnectionLibrary(metaclass=SingletonMeta):
    def __init__(self):
        self.connection_library = {}

    def check_port_exists(self, port):
        return port in self.connection_library.keys()

    def add_connection(self, connection_name, connection_list):
        for port, type in connection_list.items():
            if not isinstance(port, str):
                raise ValueError(
                    f"{connection_name} must be made out of ports with name of type string."
                )
            if not isinstance(type, int) and not isinstance(type, str):
                raise ValueError(
                    f"{connection_name} must be made out of ports with types int or string"
                )
            if isinstance(type, str):
                if type not in self.connection_library.keys():
                    raise ValueError(
                        f"Port {port} of type {type} within {connection_name} must exist within the connection library."
                    )
            if isinstance(type, int):
                if type <= 0:
                    raise ValueError(
                        f"Port {port} of width {type} within {connection_name} must have a width greater than 0"
                    )
        self.connection_library[connection_name] = connection_list

    def to_json(self, filename):
        with open("generated_files/" + filename + ".json", "w") as outfile:
            json.dump(self.connection_library, outfile, indent=4)

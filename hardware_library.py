from typing import Dict, List, Union
import json


class SingletonMeta(type):
    """
    This is a singleton metaclass.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class HardwareLibrary(metaclass=SingletonMeta):
    def __init__(self):
        self.hardware_library = {}

    def add_module(
        self,
        module_name: str,
        input_ports: Dict[str, Union[str, int]],
        output_ports: Dict[str, Union[str, int]],
    ) -> None:
        """
        Adds a module to the hardware library.

        Parameters:
        - module_name (str): The name of the module to add
        - input_ports (Dict[str, Union[str, int]]): A dictionary of input ports for the module. Keys must be strings,
            values must be strings or integers greater than zero.
        - output_ports (Dict[str, Union[str, int]]): A dictionary of output ports for the module. Keys must be strings,
            values must be strings or integers greater than zero.
        """
        if not isinstance(module_name, str):
            raise TypeError("module_name must be a string")

        if module_name in self.hardware_library:
            raise ValueError(f"Module with name {module_name} already exists")

        self._check_input_ports(input_ports)
        self._check_output_ports(output_ports)
        self._check_ports_overlap(input_ports=input_ports, output_ports=output_ports)

        module_dict = {"input_ports": input_ports, "output_ports": output_ports}

        self.hardware_library[module_name] = module_dict

    def update_module(
        self,
        module_name: str,
        input_ports: Dict[str, Union[str, int]],
        output_ports: Dict[str, Union[str, int]],
    ) -> None:
        """
        Updates a module in the hardware library.

        Parameters:
        - module_name (str): The name of the module to update
        - input_ports (Dict[str, Union[str, int]]): A dictionary of input ports for the module. Keys must be strings,
            values must be strings or integers greater than zero.
        - output_ports (Dict[str, Union[str, int]]): A dictionary of output ports for the module. Keys must be strings,
            values must be strings or integers greater than zero.
        """
        if not isinstance(module_name, str):
            raise TypeError("module_name must be a string")

        if module_name not in self.hardware_library:
            raise ValueError(f"No module with name {module_name} exists")

        self._check_input_ports(input_ports)
        self._check_output_ports(output_ports)

        self.hardware_library[module_name]["input_ports"] = input_ports
        self.hardware_library[module_name]["output_ports"] = output_ports

    def delete_module(self, module_name: str) -> None:
        """
        Deletes a module from the hardware library.

        Parameters:
        - module_name (str): The name of the module to delete
        """
        if not isinstance(module_name, str):
            raise TypeError("module_name must be a string")

        if module_name not in self.hardware_library:
            raise ValueError(f"No module with name {module_name} exists")

        del self.hardware_library[module_name]

    def _check_input_ports(self, input_ports: Dict[str, Union[str, int]]) -> None:
        """
        Check that input_ports dictionary contains only string keys and either int or string values greater than 0.

        Args:
        - input_ports: A dictionary containing input ports and their data types.

        Raises:
        - TypeError: If input_ports is not a dictionary or its keys/values are not the correct types.
        - ValueError: If any of the values of the input_ports are not strings or integers greater than 0.
        """
        if not isinstance(input_ports, dict):
            raise TypeError("Input ports must be a dictionary.")
        for key, value in input_ports.items():
            if not isinstance(key, str):
                raise TypeError("Input port keys must be strings.")
            if not isinstance(value, (str, int)):
                raise ValueError(
                    "Input port values must be strings or integers greater than 0."
                )
            if isinstance(value, int) and value <= 0:
                raise ValueError("Input port values must be integers greater than 0.")

    def _check_output_ports(self, output_ports: Dict[str, Union[str, int]]) -> None:
        """
        Check that output_ports dictionary contains only string keys and either int or string values greater than 0.

        Args:
        - output_ports: A dictionary containing output ports and their data types.

        Raises:
        - TypeError: If output_ports is not a dictionary or its keys/values are not the correct types.
        - ValueError: If any of the values of the output_ports are not strings or integers greater than 0.
        """
        if not isinstance(output_ports, dict):
            raise TypeError("Output ports must be a dictionary.")
        for key, value in output_ports.items():
            if not isinstance(key, str):
                raise TypeError("Output port keys must be strings.")
            if not isinstance(value, (str, int)):
                raise ValueError(
                    "Output port values must be strings or integers greater than 0."
                )
            if isinstance(value, int) and value <= 0:
                raise ValueError("Output port values must be integers greater than 0.")

    def to_json(self, filename):
        with open(filename, "w") as outfile:
            json.dump(self.hardware_library, outfile, indent=4)

    @staticmethod
    def from_json(filename):
        with open(filename, "r") as infile:
            hw_dict = json.load(infile)
            library = HardwareLibrary()
            library.hardware_library = hw_dict
            return library

    def format_input_list(self, module_name):
        formatted_input_list = {}
        for input in self.hardware_library[module_name]["input_ports"]:
            formatted_input_list[input] = ""
        return formatted_input_list

    def format_output_list(self, module_name):
        formatted_output_list = {}
        for output in self.hardware_library[module_name]["output_ports"]:
            formatted_output_list[output] = ""
        return formatted_output_list

    def _check_ports_overlap(self, input_ports, output_ports):
        """
        Check if the keys in input_ports and output_ports overlap.
        Raises a ValueError if any keys are shared between the two dictionaries.
        """
        if set(input_ports.keys()).intersection(set(output_ports.keys())):
            raise ValueError("Input and output ports cannot share a similar key name")

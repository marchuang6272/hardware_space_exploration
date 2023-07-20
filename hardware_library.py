from typing import Dict, List, Union
import json
import os
import re
from config import config
from singleton_meta import SingletonMeta
from connection_library import ConnectionLibrary
import networkx as nx
from networkx.readwrite import json_graph

connection_library = ConnectionLibrary()


class HardwareLibrary(metaclass=SingletonMeta):
    def __init__(self):
        self.hardware_library = {}
        self._parse_basic_verilog_files(
            config["path"] + "/hardware_modules/basic_blocks"
        )

    def __getitem__(self, key):
        return self.hardware_library[key]

    def __setitem__(self, key, value):
        self.hardware_library[key] = value

    def __delitem__(self, key):
        del self.hardware_library[key]

    def add_module(
        self,
        module_name: str,
        input_ports: Dict[str, Union[str, int]],
        output_ports: Dict[str, Union[str, int]],
        input_connections={},
        output_connections={},
        internal_graph=None,
    ) -> None:
        """
        Adds a module to the hardware library.

        Parameters:
            module_name (str): The name of the module to add.
            input_ports (Dict[str, Union[str, int]]): A dictionary of input ports for the module.
                Keys must be strings, values must be strings or integers greater than zero.
            output_ports (Dict[str, Union[str, int]]): A dictionary of output ports for the module.
                Keys must be strings, values must be strings or integers greater than zero.
            input_connections (dict, optional): A dictionary representing the input connections for the module.
                Defaults to an empty dictionary.
            output_connections (dict, optional): A dictionary representing the output connections for the module.
                Defaults to an empty dictionary.
            internal_graph (networkx.DiGraph, optional): The internal graph representation of the module.
                Defaults to None.

        Raises:
            TypeError: If module_name is not a string.
            ValueError: If a module with the same name already exists, or if the input or output ports are invalid,
                or if input or output connections refer to non-existent ports.
        """
        if not isinstance(module_name, str):
            raise TypeError("module_name must be a string")

        if module_name in self.hardware_library:
            raise ValueError(f"Module with name {module_name} already exists")

        self._check_input_ports(input_ports)
        self._check_output_ports(output_ports)
        self._check_ports_overlap(input_ports=input_ports, output_ports=output_ports)
        self._check_ports_exist(input_ports)
        self._check_ports_exist(output_ports)

        if internal_graph:
            for input_port, port_connections in input_connections.items():
                if input_port not in input_ports.keys():
                    raise ValueError(
                        f"Input port with name {input_port} not found in the declared input ports for this module"
                    )
            for output_port, port_connections in output_connections.items():
                if output_port not in output_ports.keys():
                    raise ValueError(
                        f"Output port with name {output_port} not found in the declared output ports for this module"
                    )
            internal_graph.add_input_output(
                input_ports=input_ports,
                output_ports=output_ports,
                input_connections=input_connections,
                output_connections=output_connections,
            )
        module_dict = {
            "input_ports": input_ports,
            "output_ports": output_ports,
            "basic_block": False if internal_graph else True,
            "internal_graph": nx.node_link_data(internal_graph)
            if internal_graph
            else None,
        }

        self.hardware_library[module_name] = module_dict

    def get_module_nx_graph(self, module_name):
        """
        Retrieves the networkx graph object for a specific module in the HDLGraph.

        Parameters:
            module_name (str): The name of the module.

        Returns:
            networkx.Graph: The networkx graph object representing the internal graph of the module.

        Raises:
            TypeError: If module_name is not a string.
            ValueError: If no module with the given name exists or if the module has no submodules.
        """
        if not isinstance(module_name, str):
            raise TypeError("module_name must be a string")

        if module_name not in self.hardware_library:
            raise ValueError(f"No module with name {module_name} exists")

        return nx.node_link_graph(self.hardware_library[module_name]["internal_graph"])

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

    def _parse_basic_verilog_files(self, folder_path):
        """
        Read the basic block folder, use regular expressions to extract module information to load into the hardware library

        Args:
        - folder_path - folder path to the basic block modules
        """
        # Go through all the files within the basic block folder with the .sv extension
        verilog_files = [f for f in os.listdir(folder_path) if f.endswith(".sv")]

        for file_name in verilog_files:
            module_name = ""
            input_ports = {}
            output_ports = {}

            # Read through each file in the basic block folder
            with open(os.path.join(folder_path, file_name), "r") as file:
                file_content = file.read()

                # Find the module name
                module_match = re.search(r"module\s+(\w+)\s*\(", file_content)

                if module_match:
                    # isolate the module name
                    module_name = module_match.group(1)

                    # Find all input and output ports using regular expressions
                    input_matches = re.findall(
                        r"input\s+(?:logic)?\s*(?:\[(\d+):\d+\])?\s*(?:\w+\s+)?(\w+)",
                        file_content,
                    )
                    output_matches = re.findall(
                        r"output\s+(?:logic)?\s*(?:\[(\d+):\d+\])?\s*(?:\w+\s+)?(\w+)",
                        file_content,
                    )

                    # Handle the case whether or not the port has a integer type width or a custom defined type
                    for bit_width, port_name in input_matches:
                        port_name = port_name.strip()
                        if bit_width:
                            bit_width = int(bit_width) + 1
                        else:
                            custom_type_match = re.search(
                                r"input\s+(?:logic)?\s*\w+\s+(\w+)\s*" + port_name,
                                file_content,
                            )
                            bit_width = (
                                custom_type_match.group(1) if custom_type_match else 1
                            )
                        if isinstance(bit_width, str):
                            self._check_ports_exist({port_name: bit_width})
                        input_ports[port_name] = bit_width

                    # Handle the case for output ports
                    for bit_width, port_name in output_matches:
                        port_name = port_name.strip()
                        if bit_width:
                            bit_width = int(bit_width) + 1
                        else:
                            custom_type_match = re.search(
                                r"output\s+(?:logic)?\s*\w+\s+(\w+)\s*" + port_name,
                                file_content,
                            )
                            bit_width = (
                                custom_type_match.group(1) if custom_type_match else 1
                            )
                        if isinstance(bit_width, str):
                            self._check_ports_exist({port_name: bit_width})
                        output_ports[port_name] = bit_width
            # Add the module to the hardware_library
            self.hardware_library[module_name] = {
                "input_ports": input_ports,
                "output_ports": output_ports,
                "basic_block": True,
                "internal_graph": None,
            }

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

    def _check_ports_exist(self, ports):
        """
        Check if the ports specified in the given dictionary exist in the connection library.

        Args:
            ports (dict): A dictionary where the keys represent the port names, and the values
                        represent the corresponding connection types.

        Raises:
            ValueError: If a port specified in the dictionary does not exist in the connection library.

        """
        for port, type in ports.items():
            if isinstance(type, str) and not connection_library.check_port_exists(type):
                raise ValueError(
                    f"Port with name {type} does not exist in the connection library."
                )

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

    def verify_module_exists(self, module_name):
        if module_name not in self.hardware_library.keys():
            return False
        else:
            return True

    def verify_port_exists(self, module_name, port_name, port_type):
        if module_name not in self.hardware_library.keys():
            raise ValueError(module_name + " not found in hardware_library")
        if port_type != "input" and port_type != "output":
            raise ValueError(
                '"port_type" variable needs to be either "input" or "output"'
            )

        if (
            port_type == "input"
            and port_name in self.hardware_library[module_name]["input_ports"].keys()
        ):
            return True
        if (
            port_type == "output"
            and port_name in self.hardware_library[module_name]["output_ports"].keys()
        ):
            return True
        return False

    def verify_port_type(
        self,
        source_module_name,
        destination_module_name,
        source_port_name,
        destination_port_name,
    ):
        if (
            source_module_name not in self.hardware_library.keys()
            or destination_module_name not in self.hardware_library.keys()
        ):
            return False
        elif (
            self.hardware_library[source_module_name]["output_ports"][source_port_name]
            != self.hardware_library[destination_module_name]["input_ports"][
                destination_port_name
            ]
        ):
            return False
        else:
            return True

    def to_json(self, filename):
        with open("generated_files/" + filename + ".json", "w") as outfile:
            json.dump(self.hardware_library, outfile, indent=4)

    @staticmethod
    def from_json(filename):
        with open(filename, "r") as infile:
            hw_dict = json.load(infile)
            library = HardwareLibrary()
            library.hardware_library = hw_dict
            return library

    def _check_ports_overlap(self, input_ports, output_ports):
        """
        Check if the keys in input_ports and output_ports overlap.
        Raises a ValueError if any keys are shared between the two dictionaries.
        """
        if set(input_ports.keys()).intersection(set(output_ports.keys())):
            raise ValueError("Input and output ports cannot share a similar key name")

    def get_hardware_library(self):
        return self.hardware_library

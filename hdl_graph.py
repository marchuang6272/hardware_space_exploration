import os
import string
import random
import string
import networkx as nx
import json
from config import config
from hardware_library import HardwareLibrary
from connection_library import ConnectionLibrary
import copy
from config import config
from pyvis.network import Network
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
import secrets
import file_output_loader

hardware_library = HardwareLibrary()


class HDLGraph(nx.DiGraph):
    @classmethod
    def from_hardware_library_module(HDLGraph, module_name: str) -> "HDLGraph":
        """
        Creates an instance of HDLGraph from a hardware library module.

        Parameters:
            module_name (str): The name of the module in the hardware library.

        Returns:
            HDLGraph: An instance of HDLGraph representing the specified hardware library module.

        Raises:
            ValueError: If the module with the given name does not exist in the hardware library.
        """
        module_graph = hardware_library.get_module_nx_graph(module_name)
        return HDLGraph(module_graph)

    @classmethod
    def return_expanded_graph(HDLGraph, top_module_name):
        module_graph = hardware_library.get_module_nx_graph(top_module_name)
        for node in module_graph.nodes():
            if node == "INPUT_BLOCK" or node == "OUTPUT_BLOCK":
                continue
            else:
                module_name = module_graph.nodes[node]["module_name"]
                if not hardware_library[module_name]["basic_block"]:
                    # print(node)
                    # return expanded hdl graph
                    expanded_node_graph = HDLGraph.return_expanded_graph(
                        top_module_name=module_name
                    )
                    # union together
                    module_graph = nx.union(
                        module_graph, expanded_node_graph, rename=("", node + "__")
                    )
                    expanded_outputs = module_graph.in_edges(
                        node + "__OUTPUT_BLOCK", data=True
                    )
                    # print("-----")
                    # print(module_graph.out_edges(node + "__INPUT_BLOCK", data=True))
                    expanded_inputs = module_graph.out_edges(
                        node + "__INPUT_BLOCK", data=True
                    )
                    # print("-----")
                    # print(module_graph.in_edges(node + "__OUTPUT_BLOCK", data=True))
                    for (
                        source_module,
                        destination_module,
                        data,
                    ) in module_graph.out_edges(node, data=True):
                        for source, destination in data["port_connections"].items():
                            # print(source)
                            # print(destination)
                            for (
                                expanded_source,
                                expanded_destination,
                                data,
                            ) in expanded_outputs:
                                # print(data["port_connections"])
                                for key, value in data["port_connections"].items():
                                    if source == value:
                                        # print(
                                        #     expanded_source
                                        #     + " "
                                        #     + key
                                        #     + " "
                                        #     + destination_module
                                        #     + " "
                                        #     + destination
                                        # )
                                        module_graph.add_edge(
                                            expanded_source,
                                            destination_module,
                                            port_connections={key: destination},
                                        )
                    for (
                        source_module,
                        destination_module,
                        data,
                    ) in module_graph.in_edges(node, data=True):
                        for source, destination in data["port_connections"].items():
                            # print(source)
                            # print(destination)
                            for (
                                expanded_source,
                                expanded_destination,
                                data,
                            ) in expanded_inputs:
                                # print(data["port_connections"])
                                for key, value in data["port_connections"].items():
                                    if destination == key:
                                        # print(
                                        #     expanded_destination
                                        #     + " "
                                        #     + value
                                        #     + " "
                                        #     + source_module
                                        #     + " "
                                        #     + source
                                        # )
                                        module_graph.add_edge(
                                            source_module,
                                            expanded_destination,
                                            port_connections={source: value},
                                        )

                    module_graph.remove_node(node)
                    module_graph.remove_node(node + "__INPUT_BLOCK")
                    module_graph.remove_node(node + "__OUTPUT_BLOCK")
        nodes_to_delete = [
            node for node in module_graph if module_graph.degree(node) == 0
        ]
        module_graph.remove_nodes_from(nodes_to_delete)

        return HDLGraph(module_graph)

    def add_hardware_node(self, instance_name, module_name, **attr):
        """
        Adds a node to the hardware library.

        Args:
            instance_name (str): The name of the instance to be added.
            module_name (str): The name of the module associated with the instance.
            **attr: Additional attributes to be assigned to the node.

        Returns:
            None

        Raises:
            ValueError: If the specified module does not exist in the hardware library.

        """
        if hardware_library.verify_module_exists(module_name=module_name):
            return super().add_node(instance_name, module_name=module_name, **attr)
        else:
            run_python_file("/hardware_modules/non_basic_blocks/" + module_name + ".py")
            if hardware_library.verify_module_exists(module_name=module_name):
                return super().add_node(instance_name, module_name=module_name, **attr)
            else:
                raise ValueError(
                    "Module of name "
                    + module_name
                    + " does not exist in the hardware library. Check if the associated file within /hardware_modules folder is correct."
                )

    def add_edge(
        self,
        source_instance_name,
        destination_instance_name,
        port_connections,
        **attr,
    ):
        """
        Adds an edge between two instances in the hardware library graph.

        Args:
            source_instance_name (str): The name of the source instance.
            destination_instance_name (str): The name of the destination instance.
            port_connections (dict): A dictionary mapping source ports to destination ports.
            **attr: Additional keyword arguments for the edge.

        Raises:
            ValueError: If the source instance is not instantiated as a node.
            ValueError: If the destination instance is not instantiated as a node.
            ValueError: If a source port is not found in the source module.
            ValueError: If a destination port is not found in the destination module.
            ValueError: If the source port and destination port do not have matching port types.
            ValueError: If the destination port is already driven by another signal.

        Note:
            This function extends the functionality of the super class's 'add_edge' method and
            verifies the validity of the input connections.

        """

        if not self.has_node(source_instance_name):
            raise ValueError(source_instance_name + " not instantiated as a node")
        if not self.has_node(destination_instance_name):
            raise ValueError(destination_instance_name + " not instantiated as a node")

        source_module_name = self.nodes[source_instance_name]["module_name"]
        destination_module_name = self.nodes[destination_instance_name]["module_name"]

        if self.has_edge(source_instance_name, destination_instance_name):
            current_port_connections = self.get_edge_data(
                source_instance_name, destination_instance_name
            )["port_connections"]
        else:
            current_port_connections = {}

        for source_port, destination_port in port_connections.items():
            if not hardware_library.verify_port_exists(
                source_module_name,
                source_port,
                "output",
            ):
                raise ValueError(
                    source_port + " not found in " + source_module_name + " module"
                )
            if not hardware_library.verify_port_exists(
                destination_module_name,
                destination_port,
                "input",
            ):
                raise ValueError(
                    destination_port
                    + " not found in "
                    + destination_module_name
                    + " module"
                )
            if not hardware_library.verify_port_type(
                source_module_name,
                destination_module_name,
                source_port,
                destination_port,
            ):
                raise ValueError(
                    source_port
                    + " in "
                    + source_module_name
                    + " and "
                    + destination_port
                    + " in "
                    + destination_module_name
                    + " do not have matching port types."
                )
            if not self._verify_already_driven_ports(
                destination_instance_name, destination_port
            ):
                raise ValueError(
                    destination_port
                    + " in "
                    + destination_instance_name
                    + " is already driven by another signal"
                )
            current_port_connections[source_port] = destination_port

        super().add_edge(
            source_instance_name,
            destination_instance_name,
            port_connections=current_port_connections,
            **attr,
        )

    def add_input_output(
        self, input_ports, output_ports, input_connections, output_connections
    ):
        input_block_name = config["input_block_name"]
        output_block_name = config["output_block_name"]
        alphabet = string.ascii_letters + string.digits
        temp_output_module_id = (
            output_block_name
            + "_"
            + "".join(secrets.choice(alphabet) for _ in range(8))
        )
        temp_input_module_id = (
            input_block_name + "_" + "".join(secrets.choice(alphabet) for _ in range(8))
        )

        hardware_library.add_module(
            module_name=temp_output_module_id, input_ports=output_ports, output_ports={}
        )
        hardware_library.add_module(
            module_name=temp_input_module_id, input_ports={}, output_ports=input_ports
        )

        self.add_hardware_node(
            module_name=temp_input_module_id, instance_name=input_block_name
        )
        self.add_hardware_node(
            module_name=temp_output_module_id, instance_name=output_block_name
        )

        for input_port, connections in input_connections.items():
            for module, port in connections:
                self.add_edge(
                    input_block_name, module, port_connections={input_port: port}
                )
        for output_port, connection in output_connections.items():
            module, port = connection
            self.add_edge(
                module, output_block_name, port_connections={port: output_port}
            )

        hardware_library.delete_module(module_name=temp_input_module_id)
        hardware_library.delete_module(module_name=temp_output_module_id)

        self.nodes[input_block_name]["module_name"] = input_block_name
        self.nodes[output_block_name]["module_name"] = output_block_name

    def _verify_already_driven_ports(self, instance_name, port_name):
        if not self.has_node(instance_name):
            raise ValueError(instance_name + " not instantiated in hardware library")

        # Find incoming edges to a node and access edge data
        incoming_edges = self.in_edges(instance_name, data=True)

        # Iterate over incoming edges and access edge data
        for edge in incoming_edges:
            source_node, target_node, edge_data = edge
            port_connections = edge_data["port_connections"]
            if port_name in port_connections.values():
                return False

        return True

    def to_json(self, filename):
        with open("generated_files/" + filename + ".json", "w") as outfile:
            json.dump(nx.node_link_data(self), outfile, indent=4)


def run_python_file(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = script_dir + filename

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file '{filename}' does not exist.")

    with open(file_path, "r") as file:
        code = file.read()
        exec(code)

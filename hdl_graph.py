import os
import random
import string
import networkx as nx
import json
from hardware_library import HardwareLibrary
from connection_library import ConnectionLibrary
import copy
import matplotlib.pyplot as plt
from pyvis.network import Network
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader

hardware_library = HardwareLibrary()


class HDLGraph(nx.DiGraph):
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
            raise ValueError(
                "Module of name "
                + module_name
                + " does not exist in the hardware library."
            )

    def add_edge(
        self, source_instance_name, destination_instance_name, port_connections, **attr
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
                source_module_name, source_port, "output"
            ):
                raise ValueError(
                    source_port + " not found in " + source_module_name + " module"
                )
            if not hardware_library.verify_port_exists(
                destination_module_name, destination_port, "input"
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
        # print(nx.node_link_data(self))

    def display_verilog(self, output_file):
        # Create a Jinja2 environment with the current directory as the template loader
        env = Environment(loader=FileSystemLoader("."))

        # Define a custom Jinja2 filter to check if a value is an integer
        env.filters["is_integer"] = lambda value: isinstance(value, int)

        # Load the Jinja2 templates for connection and module generation
        connection_template = env.get_template(
            "jinja_templates/verilog_connection_template.txt"
        )
        module_template = env.get_template(
            "jinja_templates/verilog_module_template.txt"
        )
        graph = Network(
            directed=True,
            font_color="white",
            width="100%",
            height="100%",
            bgcolor="#2a3950",
        )
        # Set options for background color, node color, and edge color
        options = {
            "nodes": {
                "font": {"align": "left"},
                "color": {"background": "#016171"},
                "borderWidth": 0,
            },
            "edges": {"color": "#00e0c6", "smooth": {"type": "continuous"}},
        }

        # Convert options dictionary to JSON string
        options_str = json.dumps(options)

        # Set the options using the JSON string
        graph.set_options(options_str)
        edge_labels = []
        # Generate module instances for each node in the graph
        for node in self.nodes():
            instance_name = node
            module_name = self.nodes[node]["module_name"]
            port_connections = {}

            # Retrieve outgoing edges from the current node
            outgoing_edges = self.out_edges(node, data=True)

            # Extract port connections for outgoing edges
            for edges in outgoing_edges:
                source, destination, data = edges
                for source_port, destination_port in data["port_connections"].items():
                    connection = {
                        "internal_port": source_port,
                        "external_port": source_port,
                        "external_module": source,
                    }
                    port_connections[source_port] = connection

            # Retrieve incoming edges to the current node
            incoming_edges = self.in_edges(node, data=True)

            # Extract port connections for incoming edges
            for edges in incoming_edges:
                source, destination, data = edges
                for source_port, destination_port in data["port_connections"].items():
                    connection = {
                        "internal_port": destination_port,
                        "external_port": source_port,
                        "external_module": source,
                    }
                    port_connections[destination_port] = connection

            # Generate Verilog code for the module instance
            value = {
                "module_name": module_name,
                "instance_name": instance_name,
                "port_connections": port_connections.values(),
            }
            output = module_template.render(value)
            graph.add_node(instance_name, label=output, shape="box")

        for node in self.nodes():
            module_name = self.nodes[node]["module_name"]

            # Retrieve outgoing edges from the current node
            outgoing_edges = self.out_edges(node, data=True)

            # Extract port connections and their corresponding types
            for edges in outgoing_edges:
                source, destination, data = edges
                edge_label = ""
                for port in data["port_connections"].keys():
                    type = hardware_library.hardware_library[module_name][
                        "output_ports"
                    ][port]

                    value = {"module": node, "port": port, "type_value": type}
                    output = connection_template.render(
                        module=node, port=port, type=type
                    )
                    edge_label = edge_label + output
                graph.add_edge(
                    source,
                    destination,
                    label=edge_label,
                    length=700,
                    font={"color": "white", "strokeWidth": "0px"},
                )

        graph.write_html("generated_files/" + output_file + ".html")

    def generate_verilog(self, output_file):
        """
        Generate Verilog port connections and module instances based on the provided input dictionary.
        Write the generated Verilog code to the specified output file.

        Args:
            output_file (str): The name of the output file to write the generated Verilog code.

        Returns:
            None

        Raises:
            None
        """

        # Create a Jinja2 environment with the current directory as the template loader
        env = Environment(loader=FileSystemLoader("."))

        # Define a custom Jinja2 filter to check if a value is an integer
        env.filters["is_integer"] = lambda value: isinstance(value, int)

        # Load the Jinja2 templates for connection and module generation
        connection_template = env.get_template(
            "jinja_templates/verilog_connection_template.txt"
        )
        module_template = env.get_template(
            "jinja_templates/verilog_module_template.txt"
        )

        # Open the output file for writing
        with open("generated_files/" + output_file + ".sv", "w") as file:
            # Generate port connections for each node in the graph
            for node in self.nodes():
                output_set = {}
                module_name = self.nodes[node]["module_name"]

                # Retrieve outgoing edges from the current node
                outgoing_edges = self.out_edges(node, data=True)

                # Extract port connections and their corresponding types
                for edges in outgoing_edges:
                    source, target, data = edges
                    for port in data["port_connections"].keys():
                        output_set[port] = hardware_library.hardware_library[
                            module_name
                        ]["output_ports"][port]

                # Generate Verilog code for each port connection
                for port, type in output_set.items():
                    value = {"module": node, "port": port, "type_value": type}
                    output = connection_template.render(
                        module=node, port=port, type=type
                    )
                    file.write(output)

            # Generate module instances for each node in the graph
            for node in self.nodes():
                instance_name = node
                module_name = self.nodes[node]["module_name"]
                port_connections = {}

                # Retrieve outgoing edges from the current node
                outgoing_edges = self.out_edges(node, data=True)

                # Extract port connections for outgoing edges
                for edges in outgoing_edges:
                    source, destination, data = edges
                    for source_port, destination_port in data[
                        "port_connections"
                    ].items():
                        connection = {
                            "internal_port": source_port,
                            "external_port": source_port,
                            "external_module": source,
                        }
                        port_connections[source_port] = connection

                # Retrieve incoming edges to the current node
                incoming_edges = self.in_edges(node, data=True)

                # Extract port connections for incoming edges
                for edges in incoming_edges:
                    source, destination, data = edges
                    for source_port, destination_port in data[
                        "port_connections"
                    ].items():
                        connection = {
                            "internal_port": destination_port,
                            "external_port": source_port,
                            "external_module": source,
                        }
                        port_connections[destination_port] = connection

                # Generate Verilog code for the module instance
                value = {
                    "module_name": module_name,
                    "instance_name": instance_name,
                    "port_connections": port_connections.values(),
                }
                output = module_template.render(value)
                file.write(output)

        # Print a success message after generating the Verilog file
        print(f"Verilog file '{output_file}' generated successfully.")

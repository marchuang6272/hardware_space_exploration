import os
import random
import string
import config
import networkx as nx
from encoder import Encoder
import json
from hardware_module import HardwareModule
from connection import Connection
from hardware_library import HardwareLibrary
from connection_library import CONNECTION_LIBRARY
import copy
import matplotlib.pyplot as plt
from pyvis.network import Network
from bs4 import BeautifulSoup

hardware_library = HardwareLibrary()


class HDLGraph(nx.DiGraph):
    def update_configuration(parameters):
        return

    def generate_id(self, length):
        characters = (
            string.ascii_letters + string.digits
        )  # Includes uppercase letters, lowercase letters, and digits
        id = "".join(random.choices(characters, k=length))
        return id

    def draw_graph(self):
        nx.draw(self, with_labels=True)
        nx.draw_networkx_edge_labels(
            self,
            pos=nx.spring_layout(self),
            edge_labels={("adder_instance_1", "adder_instance_2"): "yes"},
            rotate=True,
        )

    def add_node(self, node_for_adding, **attr):
        if (
            len(attr) == 1
            and "hardwareModule" in attr.keys()
            and isinstance(attr["hardwareModule"], HardwareModule)
        ):
            return super().add_node(node_for_adding, **attr)
        else:
            raise Exception(
                "You must add only a single HardwareModule object to the node"
            )

    def _add_edge(self, u_for_edge, v_for_edge, key=None, **attr):
        if len(attr) == 1 and "data" in attr.keys() and isinstance(attr["data"], dict):
            return super().add_edge(u_for_edge, v_for_edge, key=key, **attr)
        else:
            raise Exception("You must add only a single Connection object to the node")

    def add_connection_to_library(self, connection_name, component_signals):
        CONNECTION_LIBRARY[connection_name] = component_signals

    def instantiate_hardware_node(self, module_name, instance_name):
        hardware_module = HardwareModule(
            module_name=module_name, instance_name=instance_name
        )
        self.add_node(instance_name, hardwareModule=hardware_module)

    def add_connection_edge(
        self, source_module_name, destination_module_name, port_connections
    ):
        if source_module_name in self.nodes and destination_module_name in self.nodes:
            edge_info = self.get_edge_data(source_module_name, destination_module_name)
            if edge_info:
                for source_port, destination_port in port_connections.items():
                    connection = Connection(
                        source_module=self.nodes[source_module_name],
                        destination_module=self.nodes[destination_module_name],
                        source_port=source_port,
                        destination_port=destination_port,
                        key=edge_info["key"],
                    )
                edge_info["data"]["connection_list"].append(connection)

            else:
                key = self.generate_id(config.KEY_LENGTH)
                connection_list = []
                for source_port, destination_port in port_connections.items():
                    connection = Connection(
                        source_module=self.nodes[source_module_name],
                        destination_module=self.nodes[destination_module_name],
                        source_port=source_port,
                        destination_port=destination_port,
                        key=key,
                    )
                    connection_list.append(connection)
                self._add_edge(
                    source_module_name,
                    destination_module_name,
                    key=key,
                    data={"key": key, "connection_list": connection_list},
                )
        else:
            raise Exception(
                "Source or Destination module not found in instantiated node list"
            )

    def to_json(self, filename):
        with open(filename, "w") as outfile:
            json.dump(nx.node_link_data(self), outfile, cls=Encoder, indent=4)
        # print(nx.node_link_data(self))

    def inject_refresh_script(self, html_file):
        # Get the last modified timestamp of the HTML file
        last_modified = os.path.getmtime(html_file)

        # Read the HTML file
        with open(html_file, "r") as file:
            html_content = file.read()

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # Create a new <script> tag
        script_tag = soup.new_tag("script")
        script_tag.string = f"""
            var lastModified = {last_modified};
            setInterval(function() {{
                fetch("{html_file}")
                    .then(function(response) {{
                        return response.text();
                    }})
                    .then(function(html) {{
                        var parser = new DOMParser();
                        var doc = parser.parseFromString(html, 'text/html');
                        var currentModified = doc.lastModified;
                        if (currentModified !== lastModified) {{
                            location.reload();
                        }}
                    }});
            }}, 1000);
        """

        # Append the <script> tag to the <body> tag
        body_tag = soup.body
        body_tag.append(script_tag)

        # Save the modified HTML content back to the file
        with open(html_file, "w") as file:
            file.write(str(soup))

    def display(self):
        graph = Network(
            directed=True,
            font_color="white",
            width="100%",
            height="100%",
            bgcolor="#2a3950",
        )
        # Set options for background color, node color, and edge color
        options = {
            "nodes": {"color": {"background": "#016171"}, "borderWidth": 0},
            "edges": {"color": "#00e0c6", "smooth": {"type": "continuous"}},
        }

        # Convert options dictionary to JSON string
        options_str = json.dumps(options)

        # Set the options using the JSON string
        graph.set_options(options_str)
        edge_labels = []
        for node_id in self.nodes:
            node_info = self.nodes[node_id]["hardwareModule"]
            node_label = "Module Name: " + node_info.module_name + "\n"
            node_label = node_label + "Instance Name: " + node_id + "\n"
            node_label = node_label + "\nInput:\n"
            for input_port, input_port_info in node_info.input_ports.items():
                port_string = input_port_info["type"]
                if isinstance(port_string, int):
                    port_string = "[" + str(port_string - 1) + ":0]"
                node_label = node_label + port_string + " " + input_port + "\n"

            node_label = node_label + "\nOutput:\n"
            for output_port, output_port_info in node_info.output_ports.items():
                port_string = output_port_info["type"]
                if isinstance(port_string, int):
                    port_string = "[" + str(port_string - 1) + ":0]"
                node_label = node_label + port_string + " " + output_port + "\n"

            graph.add_node(node_id, label=node_label, shape="box")

        for edge_id in self.edges:
            source = edge_id[0]
            destination = edge_id[1]
            connection_list = self.edges[edge_id]["data"]["connection_list"]
            edge_label = ""
            for connection in connection_list:
                if isinstance(connection.type, int):
                    edge_label = (
                        edge_label
                        + "["
                        + str(connection.type - 1)
                        + ":0] "
                        + connection.source_port
                        + " -> "
                        + connection.destination_port
                        + "\n"
                    )
                else:
                    edge_label = (
                        edge_label
                        + connection.type
                        + " "
                        + connection.source_port
                        + " -> "
                        + connection.destination_port
                        + "\n"
                    )
            graph.add_edge(
                source,
                destination,
                label=edge_label,
                length=700,
                font={"color": "white", "strokeWidth": "0px"},
            )
        graph.write_html("templates/graph.html")

        # Usage example
        html_file_path = "templates/graph.html"
        # Analyze outgoing edges from node 'A'
        outgoing_edges = self.out_edges("multiplier_instance")

        # Print the outgoing edges
        for edge in outgoing_edges:
            source, target = edge
            print(f"Outgoing edge from {source} to {target}")
        # self.inject_refresh_script(html_file_path)
        # # Save the HTML to a file
        # with open("templates/graph.html", "w") as f:
        #     f.write(graph.html)
        #

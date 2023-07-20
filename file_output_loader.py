"""
In charge of handling any generation or visualiztion of Verilog
"""

import networkx as nx
import os
import json
from config import config
from hardware_library import HardwareLibrary
from pyvis.network import Network
from hdl_graph import HDLGraph
from jinja2 import Environment, FileSystemLoader

hardware_library = HardwareLibrary()


def display_hardware_library():
    """
    As of right now, HDLGraph() must be initialized in order to turn HardwareLibrary modules from JSON into HDLGraphs in order to
    turn those HDLGraphs into verilog files. This should be fixed.
    """
    clear_folder(config["path"] + "/generated_files/verilog")
    clear_folder(config["path"] + "/generated_files/html")
    lib = hardware_library.get_hardware_library()
    for module_name in lib.keys():
        if not lib[module_name]["basic_block"]:
            if hardware_library[module_name]["basic_block"]:
                hdl_graph = HDLGraph()
            else:
                hdl_graph = HDLGraph.from_hardware_library_module(module_name)
            generate_verilog(module_name)
            display_verilog(module_name)


def display_verilog(module_name, hdl_graph=None):
    # Create a Jinja2 environment with the current directory as the template loader
    env = Environment(loader=FileSystemLoader("."))

    # Define a custom Jinja2 filter to check if a value is an integer
    env.filters["is_integer"] = lambda value: isinstance(value, int)

    # Load the Jinja2 templates for connection and module generation
    connection_template = env.get_template(
        "jinja_templates/verilog_connection_template.txt"
    )
    if hdl_graph:
        hdl_graph = hdl_graph
    elif hardware_library[module_name]["basic_block"]:
        hdl_graph = HDLGraph()
    else:
        hdl_graph = HDLGraph.from_hardware_library_module(module_name)
    module_template = env.get_template("jinja_templates/verilog_module_template.txt")
    graph = Network(
        directed=True,
        font_color="white",
        width="100%",
        height="100%",
        bgcolor="#2a3950",
    )
    graph.options.physics.enabled = False

    # Set options for background color, node color, and edge color
    options = {
        "nodes": {
            "font": {"align": "left"},
            "color": {"background": "#016171"},
            "borderWidth": 0,
        },
        "edges": {
            "font": {"align": "vertical"},
            "color": "#00e0c6",
            "smooth": {"type": "continuous"},
        },
    }

    # Convert options dictionary to JSON string
    options_str = json.dumps(options)

    # Set the options using the JSON string
    graph.set_options(options_str)
    edge_labels = []
    pos = nx.spring_layout(hdl_graph, scale=700)
    # Generate module instances for each node in the graph
    for node in hdl_graph.nodes():
        instance_name = node
        module = hdl_graph.nodes[node]["module_name"]
        port_connections = {}

        # Retrieve outgoing edges from the current node
        outgoing_edges = hdl_graph.out_edges(node, data=True)

        # Extract port connections for outgoing edges
        for edges in outgoing_edges:
            source, destination, data = edges
            for source_port, destination_port in data["port_connections"].items():
                if destination == config["output_block_name"]:
                    connection = {
                        "internal_port": source_port,
                        "external_port": destination_port,
                        "external_module": destination,
                    }
                else:
                    connection = {
                        "internal_port": source_port,
                        "external_port": source_port,
                        "external_module": source,
                    }
                port_connections[source_port] = connection

        # Retrieve incoming edges to the current node
        incoming_edges = hdl_graph.in_edges(node, data=True)

        # Extract port connections for incoming edges
        for edges in incoming_edges:
            source, destination, data = edges
            for source_port, destination_port in data["port_connections"].items():
                if destination == config["output_block_name"]:
                    connection = {
                        "internal_port": destination_port,
                        "external_port": source_port,
                        "external_module": destination,
                    }
                else:
                    connection = {
                        "internal_port": destination_port,
                        "external_port": source_port,
                        "external_module": source,
                    }
                port_connections[destination_port] = connection

        # Generate Verilog code for the module instance
        value = {
            "input_block_name": config["input_block_name"],
            "output_block_name": config["output_block_name"],
            "module_name": module,
            "instance_name": instance_name,
            "port_connections": port_connections.values(),
        }
        output = module_template.render(value)
        if (
            instance_name == config["input_block_name"]
            or instance_name == config["output_block_name"]
        ):
            graph.add_node(
                instance_name,
                label=output,
                shape="box",
                x=1.5 * pos[instance_name][0],
                y=0,
                fixed=False,
                color=config["input_output_block_color"],
                physics=False,
            )
        elif hardware_library.get_hardware_library()[module]["basic_block"]:
            graph.add_node(
                instance_name,
                label=output,
                shape="box",
                x=1.5 * pos[instance_name][0],
                y=2 * pos[instance_name][1],
                color=config["basic_block_color"],
                fixed=False,
                physics=False,
            )

        else:
            graph.add_node(
                instance_name,
                label=output,
                shape="box",
                title="<a href="
                + config["verilog_visualization_base_url"]
                + module
                + "'>VIEW",
                x=1.5 * pos[instance_name][0],
                y=2 * pos[instance_name][1],
                fixed=False,
                physics=False,
            )

    for node in hdl_graph.nodes():
        module = hdl_graph.nodes[node]["module_name"]

        # Retrieve outgoing edges from the current node
        outgoing_edges = hdl_graph.out_edges(node, data=True)

        # Extract port connections and their corresponding types
        for edges in outgoing_edges:
            source, destination, data = edges
            # Done so that any modules outputting to an output block has an edge that correct interfaces with the output_port
            if destination == config["output_block_name"]:
                module_param = destination
            else:
                module_param = node
            edge_label = ""
            for port in data["port_connections"].keys():
                type = (
                    hardware_library.hardware_library[module]["output_ports"][port]
                    if (
                        module != config["input_block_name"]
                        and module != config["output_block_name"]
                    )
                    else ""
                )
                output = connection_template.render(
                    module=module_param,
                    port=port,
                    type=type,
                    input_block_name=config["input_block_name"],
                    output_block_name=config["output_block_name"],
                )
                edge_label = edge_label + output
            if (
                source == config["input_block_name"]
                or destination == config["output_block_name"]
            ):
                graph.add_edge(
                    source,
                    destination,
                    label=edge_label,
                    label_angle=45,
                    length=700,
                    color=config["input_output_edge_color"],
                    font={"color": "white", "strokeWidth": "0px"},
                )
            else:
                graph.add_edge(
                    source,
                    destination,
                    label=edge_label,
                    label_angle=45,
                    length=700,
                    font={"color": "white", "strokeWidth": "0px"},
                )

    graph.write_html("generated_files/html/" + module_name + ".html")
    del hdl_graph


def generate_verilog(module_name, hdl_graph=None):
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
    env.trim_blocks = True
    env.lstrip_blocks = True

    # Define a custom Jinja2 filter to check if a value is an integer
    env.filters["is_integer"] = lambda value: isinstance(value, int)

    # Load the Jinja2 templates for connection and module generation
    connection_template = env.get_template(
        "jinja_templates/verilog_connection_template.txt"
    )
    module_template = env.get_template("jinja_templates/verilog_module_template.txt")
    input_output_template = env.get_template(
        "jinja_templates/verilog_module_input_output.txt"
    )
    if hdl_graph:
        hdl_graph = hdl_graph
    elif hardware_library[module_name]["basic_block"]:
        hdl_graph = HDLGraph()
    else:
        hdl_graph = HDLGraph.from_hardware_library_module(module_name)
    # Open the output file for writing
    with open("generated_files/verilog/" + module_name + ".sv", "w") as file:
        library_module = hardware_library.get_hardware_library()[module_name]
        input_ports = library_module["input_ports"]
        output_ports = library_module["output_ports"]
        port_connections = {}
        for port_name, type in input_ports.items():
            port_connections[port_name] = {"type": type, "input_output": "input"}
        for port_name, type in output_ports.items():
            port_connections[port_name] = {"type": type, "input_output": "output"}
        value = {"module_name": module_name, "port_connections": port_connections}
        output = input_output_template.render(
            module_name=module_name, port_connections=port_connections
        )
        file.write(output)
        # Generate port connections for each node in the graph
        for node in hdl_graph.nodes():
            module_name = hdl_graph.nodes[node]["module_name"]
            if (
                node == config["input_block_name"]
                or node == config["output_block_name"]
            ):
                continue
            output_set = {}

            # Retrieve outgoing edges from the current node
            outgoing_edges = hdl_graph.out_edges(node, data=True)
            # Extract port connections and their corresponding types
            for edges in outgoing_edges:
                source, target, data = edges
                for port in data["port_connections"].keys():
                    output_set[port] = (
                        hardware_library.hardware_library[module_name]["output_ports"][
                            port
                        ]
                        if (
                            module_name != config["input_block_name"]
                            and module_name != config["output_block_name"]
                        )
                        else ""
                    )

            # Generate Verilog code for each port connection
            for port, type in output_set.items():
                value = {"module": node, "port": port, "type_value": type}
                output = connection_template.render(module=node, port=port, type=type)
                file.write(output)

        # Generate module instances for each node in the graph
        for node in hdl_graph.nodes():
            module_name = hdl_graph.nodes[node]["module_name"]
            if (
                node == config["input_block_name"]
                or node == config["output_block_name"]
            ):
                continue
            instance_name = node
            port_connections = {}

            # Retrieve outgoing edges from the current node
            outgoing_edges = hdl_graph.out_edges(node, data=True)

            # Extract port connections for outgoing edges
            for edges in outgoing_edges:
                source, destination, data = edges
                for source_port, destination_port in data["port_connections"].items():
                    if destination == config["output_block_name"]:
                        connection = {
                            "internal_port": source_port,
                            "external_port": destination_port,
                            "external_module": destination,
                        }
                    else:
                        connection = {
                            "internal_port": source_port,
                            "external_port": source_port,
                            "external_module": source,
                        }
                    port_connections[source_port] = connection

            # Retrieve incoming edges to the current node
            incoming_edges = hdl_graph.in_edges(node, data=True)

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
                "input_block_name": config["input_block_name"],
                "output_block_name": config["output_block_name"],
                "module_name": module_name,
                "instance_name": instance_name,
                "port_connections": port_connections.values(),
            }
            output = module_template.render(value)
            file.write(output)
        file.write("endmodule")
    del hdl_graph


def clear_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            os.rmdir(dir_path)
    return

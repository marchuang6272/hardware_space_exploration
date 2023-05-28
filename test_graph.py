import networkx as nx
from connection_library import ConnectionLibrary
import matplotlib.pyplot as plt
from hdl_graph import HDLGraph
from hardware_library import HardwareLibrary
import random
from pyvis.network import Network
import json
from networkx.readwrite import json_graph


g = HDLGraph()
hardware_library = HardwareLibrary()
connection_library = ConnectionLibrary()
connection_library.add_connection("intermediate", {"a": 8, "b": 8})
connection_library.add_connection("type", {"a": "intermediate", "b": 8})

hardware_library.add_module(
    module_name="adder",
    input_ports={"a": "intermediate", "b": "type"},
    output_ports={"run": "intermediate", "c": 8, "d": 10, "four": 8},
)

hardware_library.add_module(
    module_name="multiplier",
    input_ports={"a": "intermediate", "b": 8, "ac": 10, "input": 10, "c": 8},
    output_ports={"run": "intermediate", "product": "intermediate", "test": 8},
)

g.add_hardware_node(module_name="adder", instance_name="adder_instance_1")
g.add_hardware_node(module_name="multiplier", instance_name="multiplier_instance")
g.add_hardware_node(module_name="multiplier", instance_name="multiplier_instance_1")

g.add_edge(
    "adder_instance_1",
    "multiplier_instance",
    port_connections={
        "d": "ac",
    },
)

g.add_edge(
    "adder_instance_1",
    "multiplier_instance_1",
    port_connections={"d": "ac"},
)
# g.add_edge(
#     "multiplier_instance_1",
#     "multiplier_instance",
#     port_connections={"product": "a"},
# )
# g.add_edge(
#     "multiplier_instance",
#     "multiplier_instance_1",
#     port_connections={"product": "a"},
# )
# g.add_edge(
#     "multiplier_instance",
#     "multiplier_instance_1",
#     port_connections={"product": "a"},
# )
#     "adder_instance_1",
#     "multiplier_instance",
#     port_connections={"four": "c"},
# )
g.to_json("hardware_graph")
connection_library.to_json("connection_library")
# hardware_library.to_json("hardware_library.json")
g.generate_verilog("output_file")
g.display_verilog("display")
# # graph_converted = read_json_file("hardware_graph.json")
# # graph = Network(directed=True, width="100%", height="100%", bgcolor="#2a3950")
# # # Set options for background color, node color, and edge color
# # options = {
# #     "nodes": {"color": {"background": "#016171"}, "borderWidth": 0},
# #     "edges": {"color": "#00e0c6"},
# # }

# # # Convert options dictionary to JSON string
# # options_str = json.dumps(options)

# # # Set the options using the JSON string
# # graph.set_options(options_str)
# # graph.from_nx(graph_converted)
# g.display()

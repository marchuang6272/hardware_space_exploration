# importing networkx

# importing matplotlib.pyplot
import networkx as nx
import matplotlib.pyplot as plt
from hdl_graph import HDLGraph
from hardware_module import HardwareModule
from hardware_library import HardwareLibrary
import random
from pyvis.network import Network
import json
from networkx.readwrite import json_graph


def read_json_file(filename):
    with open(filename) as f:
        js_graph = json.load(f)
    return json_graph.node_link_graph(js_graph)


g = HDLGraph()
hardware_library = HardwareLibrary()
g.add_connection_to_library("intermediate", {"a": 8, "b": 8})

hardware_library.add_module(
    module_name="adder",
    input_ports={"a": "intermediate", "b": 8},
    output_ports={"c": 8, "d": 10, "four": 8},
)

hardware_library.add_module(
    module_name="multiplier",
    input_ports={"a": "intermediate", "b": 8, "ac": 10, "input": 10, "c": 8},
    output_ports={"product": "intermediate"},
)

top = HardwareModule(
    module_name="adder",
    instance_name="adder_top",
)
top.add_hdl_graph(hdl_graph=g)
g.instantiate_hardware_node(module_name="adder", instance_name="adder_instance_1")
g.instantiate_hardware_node(
    module_name="multiplier", instance_name="multiplier_instance"
)
g.instantiate_hardware_node(
    module_name="multiplier", instance_name="multiplier_instance_1"
)
g.add_connection_edge(
    "adder_instance_1",
    "multiplier_instance",
    port_connections={"c": "b"},
)
g.add_connection_edge(
    "adder_instance_1",
    "multiplier_instance_1",
    port_connections={"four": "b"},
)
g.add_connection_edge(
    "adder_instance_1",
    "multiplier_instance",
    port_connections={"d": "ac"},
)
g.add_connection_edge(
    "multiplier_instance_1",
    "multiplier_instance",
    port_connections={"product": "a"},
)
# g.add_connection_edge(
#     "multiplier_instance",
#     "multiplier_instance_1",
#     port_connections={"product": "a"},
# )
# g.add_connection_edge(
#     "adder_instance_1",
#     "multiplier_instance",
#     port_connections={"four": "c"},
# )
g.to_json("hardware_graph.json")
hardware_library.to_json("hardware_library.json")
top.convert_to_verilog()
# graph_converted = read_json_file("hardware_graph.json")
# graph = Network(directed=True, width="100%", height="100%", bgcolor="#2a3950")
# # Set options for background color, node color, and edge color
# options = {
#     "nodes": {"color": {"background": "#016171"}, "borderWidth": 0},
#     "edges": {"color": "#00e0c6"},
# }

# # Convert options dictionary to JSON string
# options_str = json.dumps(options)

# # Set the options using the JSON string
# graph.set_options(options_str)
# graph.from_nx(graph_converted)
g.display()

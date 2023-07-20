from hardware_library import HardwareLibrary


"""
This shows how to define a hardware module that serves to be a node
in the graph.
"""

# Instantiate the subgraph
g = HDLGraph()


"""
Instantiate the nodes within the module's subgraph. If the required
nodes does not exist, the hardware_modules folder will be searched
and the file defining the needed submodule will be ran first. This
essentially builds the hardware library "from the ground up", so that
modules are only added to the library if all of its submodules
currently exist in the library.
"""
g.add_hardware_node(module_name="adder", instance_name="adder_instance_1")
g.add_hardware_node(module_name="multiplier", instance_name="multiplier_instance")
g.add_hardware_node(module_name="multiplier", instance_name="multiplier_instance_1")
g.add_hardware_node(module_name="hen", instance_name="hen_1")

"""
Once the nodes are defined, we add connections between the nodes. Error
checking is done so that connections can only be made if the connection
is "valid", such as valid port type, valid port existance, no multiple
driven-ports, etc.
"""
g.add_edge(
    "adder_instance_1",
    "multiplier_instance",
    port_connections={
        "d": "ac",
    },
)

g.add_edge(
    "hen_1",
    "multiplier_instance_1",
    port_connections={"test": "ac"},
)
g.add_edge(
    "multiplier_instance_1",
    "hen_1",
    port_connections={"product": "fingers"},
)
g.add_edge(
    "multiplier_instance_1",
    "multiplier_instance",
    port_connections={"product": "a"},
)

"""
Finally, the graph defined above needs a name, input/output ports, and
connections to be made between the input/output ports and the internal
subgraph. This is accomplished below.
"""
hardware_library = HardwareLibrary()
hardware_library.add_module(
    module_name="top_module",
    input_ports={
        "a": 8,
        "c": 8,
        "b": 8,
    },
    output_ports={"test_run": 8, "product": 8, "test": 8},
    input_connections={
        "a": [("adder_instance_1", "a"), ("multiplier_instance_1", "cb")],
        "c": [("adder_instance_1", "cb")],
    },
    output_connections={"test_run": ("multiplier_instance", "run")},
    internal_graph=g,
)

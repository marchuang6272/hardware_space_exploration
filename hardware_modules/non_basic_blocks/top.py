from hardware_library import HardwareLibrary

g = HDLGraph()
g.add_hardware_node(module_name="adder", instance_name="adder_instance_1")
g.add_hardware_node(module_name="multiplier", instance_name="multiplier_instance")
g.add_hardware_node(module_name="multiplier", instance_name="multiplier_instance_1")
g.add_hardware_node(module_name="hen", instance_name="hen_1")
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
    port_connections={
        "test": "a",
    },
)
g.add_edge(
    "adder_instance_1",
    "multiplier_instance_1",
    port_connections={"d": "ac"},
)
g.add_edge(
    "multiplier_instance",
    "multiplier_instance_1",
    port_connections={"product": "a"},
)
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

#!/usr/bin/env python3


g = HDLGraph()
g.add_hardware_node(module_name="adder", instance_name="adder_instance_1")
g.add_hardware_node(module_name="multiplier", instance_name="multiplier_instance")
g.add_hardware_node(module_name="memory", instance_name="memory_instance_1")
g.add_edge(
    "multiplier_instance", "memory_instance_1", port_connections={"run": "memory_input"}
)
hardware_library.add_module(
    module_name="hen",
    input_ports={
        "fingers": 8,
        "adder_input": 8,
    },
    output_ports={"run": 8, "product": "intermediate", "test": 8},
    input_connections={
        "fingers": [("multiplier_instance", "cb")],
        "adder_input": [("adder_instance_1", "a")],
    },
    output_connections={
        "test": ("memory_instance_1", "test"),
    },
    internal_graph=g,
)

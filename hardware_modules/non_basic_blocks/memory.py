#!/usr/bin/env python3


g = HDLGraph()
g.add_hardware_node(module_name="multiplier", instance_name="multiplier_instance")
g.add_hardware_node(module_name="multiplier", instance_name="multiplier_instance_1")
g.add_edge(
    "multiplier_instance", "multiplier_instance_1", port_connections={"run": "cb"}
)
hardware_library.add_module(
    module_name="memory",
    input_ports={
        "memory_input": 8,
    },
    output_ports={"test": 8},
    input_connections={
        "memory_input": [("multiplier_instance", "cb")],
    },
    output_connections={
        "test": ("multiplier_instance_1", "product"),
    },
    internal_graph=g,
)

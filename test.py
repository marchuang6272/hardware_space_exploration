from pyvis.network import Network
import json
import webbrowser
from hdl_graph import HDLGraph

g = HDLGraph()
input_dict = {
    "connections": [
        {
            "source_module": "module1",
            "destination_module": "module2",
            "source_port": "port1",
            "destination_port": "port2",
            "type": "string_value",
        },
        {
            "source_module": "module3",
            "destination_module": "module4",
            "source_port": "port3",
            "destination_port": "port4",
            "type": 8,
        },
    ],
    "hardware_modules": [
        {
            "module_name": "ModuleA",
            "instance_name": "instA",
            "port_connections": [
                {
                    "internal_port": "module1",
                    "external_port": "module2",
                    "external_module": "port1",
                },
                {
                    "internal_port": "module1",
                    "external_port": "module2",
                    "external_module": "port1",
                },
            ],
        },
        {
            "module_name": "ModuleB",
            "instance_name": "instB",
            "port_connections": [
                {
                    "internal_port": "module1",
                    "external_port": "module2",
                    "external_module": "port1",
                }
            ],
        },
    ],
}

g.generate_verilog(input_dict, "output_file.sv")

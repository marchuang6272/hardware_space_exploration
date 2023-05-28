import generate_verilog
from hardware_library import HardwareLibrary
import json

hardware_library = HardwareLibrary()


class HardwareModule:
    def __init__(self, instance_name: str, module_name: str):
        self.instance_name = instance_name
        self.module_name = module_name
        self.input_ports = {}
        self.output_ports = {}

        if module_name not in hardware_library.hardware_library:
            raise ValueError(f"Module '{module_name}' not found in HardwareLibrary")

        module = hardware_library.hardware_library[module_name]
        self.input_ports = {
            k: {"type": module["input_ports"][k], "connection": ""}
            for k in module["input_ports"]
        }
        self.output_ports = {
            k: {"type": module["output_ports"][k], "connection": []}
            for k in module["output_ports"]
        }

    def get_instance_name(self):
        return self.instance_name

    def add_hdl_graph(self, hdl_graph):
        self.hdl_graph = hdl_graph

    def convert_to_verilog(self):
        generate_verilog.generate_module_header(self, "generated_verilog.sv")
        generate_verilog.convert_graph_to_verilog(
            self.hdl_graph, "generated_verilog.sv"
        )

    def add_input_connection(self, port_name, key, connection):
        if self.input_ports[port_name]["connection"]:
            raise RuntimeError(
                "Hardware module already has input port " + port_name + "taken"
            )
        else:
            self.input_ports[port_name]["connection"] = key

    def add_output_connection(self, port_name, key, connection):
        self.output_ports[port_name]["connection"].append(key)
        self.output_ports[port_name]["connection"] = list(
            set(self.output_ports[port_name]["connection"])
        )

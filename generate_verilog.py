# write_messages.py

from jinja2 import Environment, FileSystemLoader
import os
from hardware_library import HardwareLibrary


hardware_library = HardwareLibrary()
environment = Environment(
    loader=FileSystemLoader("hardware_module_templates/"),
    trim_blocks=True,
    lstrip_blocks=True,
)


def generate_module_header(hardwareModule, target_file):
    return
    # with open(target_file, mode="w", encoding="utf-8") as results:
    #     results.write("Hello")

    # intermediate_verilog_file = open("intermediate_verilog.txt",'r')
    # for line in intermediate_verilog_file:
    #     f2.write(line)
    # if os.path.exists("intermediate_verilog.txt"):
    #     os.remove("intermediate_verilog.txt")


def generate_module(
    target_file, module_name, instance_name, parameter_list_i={}, port_list_i={}
):
    module_found = False
    port_list = {}
    parameter_list = {}
    for module, value in hardware_library.hardware_library.items():
        if module == module_name:
            input_list = hardware_library.format_input_list(module_name=module)
            output_list = hardware_library.format_output_list(module_name=module)
            parameter_list = {}
            module_found = True
            for port_list_key, port_list_value in input_list.items():
                for port_list_i_key, port_list_i_value in port_list_i.items():
                    if port_list_key == port_list_i_key:
                        port_list[port_list_key] = port_list_i_value
            for port_list_key, port_list_value in output_list.items():
                for port_list_i_key, port_list_i_value in port_list_i.items():
                    if port_list_key == port_list_i_key:
                        port_list[port_list_key] = port_list_i_value

            for parameter_list_key, parameter_list_value in parameter_list.items():
                for (
                    parameter_list_i_key,
                    parameter_list_i_value,
                ) in parameter_list_i.items():
                    if parameter_list_key == parameter_list_i_key:
                        parameter_list[parameter_list_key] = parameter_list_i_value
    if module_found:
        generate_module_base(
            target_file=target_file,
            instance_name_i=instance_name,
            module_name_i=module_name,
            parameter_list_i=parameter_list,
            port_list_i=port_list,
        )


def generate_module_base(
    target_file, instance_name_i, module_name_i, parameter_list_i={}, port_list_i={}
):
    instance_name = instance_name_i
    module_name = module_name_i
    port_list = port_list_i
    parameter_list = parameter_list_i

    results_template = environment.get_template("hardware_module_base_template.txt")

    results_filename = target_file
    context = {
        "instance_name": instance_name,
        "module_name": module_name,
        "port_list": port_list,
        "parameter_list": parameter_list,
    }

    with open(target_file, mode="w", encoding="utf-8") as results:
        results.write(results_template.render(context))


def convert_verilog(
    read_file, write_file, intermediate_file="intermediate_verilog.txt"
):
    # Open the input and output files
    f1 = open(read_file, "r")
    f2 = open(write_file, "w")

    for line in f1:
        saved_line = line
        line = line.strip()

        # Check for the marker indicating injected python code
        if line and line.startswith("//+"):
            # Put filename into function call
            i = line.find("(")
            if i != -1:
                new_string = (
                    line[3 : i + 1] + '"' + intermediate_file + '",' + line[i + 1 :]
                )

            eval(new_string)
            intermediate_verilog_file = open(intermediate_file, "r")
            for line in intermediate_verilog_file:
                f2.write(line)
            if os.path.exists(intermediate_file):
                os.remove(intermediate_file)
        # If there is no injected python, just directly copy the verilog to the output file
        else:
            f2.write(saved_line)


def convert_graph_to_verilog(
    graph, write_file, intermediate_file="intermediate_verilog.txt"
):
    # Open the input and output files
    f2 = open(write_file, "w")

    connection_library = {}

    for instance_name in list(graph.edges):
        source_module = graph.nodes[instance_name[0]]["hardwareModule"]
        destination_module = graph.nodes[instance_name[1]]["hardwareModule"]
        connection_library[instance_name[0]] = {}
        connection_library[instance_name[1]] = {}
        connection = graph.edges[instance_name]
        for connection_info in connection["data"]["connection_list"]:
            source = connection_info.source_port
            destination = connection_info.destination_port
            if isinstance(source_module.output_ports[source]["type"], int):
                string_to_print = (
                    source_module.instance_name
                    + "_"
                    + source
                    + "_to_"
                    + destination_module.instance_name
                    + "_"
                    + destination
                )
                f2.write(
                    "logic "
                    + " ["
                    + str(source_module.output_ports[source]["type"] - 1)
                    + ":0] "
                    + string_to_print
                    + ";\n"
                )
            else:
                string_to_print = (
                    source_module.instance_name
                    + "_"
                    + source
                    + "_to_"
                    + destination_module.instance_name
                    + "_"
                    + destination
                )
                f2.write(
                    source_module.output_ports[source]["type"]
                    + " "
                    + string_to_print
                    + ";\n"
                )

            connection_library[source_module.instance_name][source] = string_to_print
            connection_library[destination_module.instance_name][
                destination
            ] = string_to_print

    for instance_name in list(graph.nodes):
        hardware_module = graph.nodes[instance_name]["hardwareModule"]
        generate_module(
            "intermediate_verilog.txt",
            hardware_module.module_name,
            hardware_module.instance_name,
            parameter_list_i={},
            port_list_i=connection_library[hardware_module.instance_name]
            if (hardware_module.instance_name in connection_library.keys())
            else {},
        )
        intermediate_verilog_file = open("intermediate_verilog.txt", "r")
        for line in intermediate_verilog_file:
            f2.write(line)
        if os.path.exists(intermediate_file):
            os.remove(intermediate_file)

from connection_library import ConnectionLibrary
from config import config
import networkx as nx
import os
import json
import file_output_loader
from hardware_library import HardwareLibrary
from hdl_graph import HDLGraph


"""
The File Structure

test_graph.py - The default file that is run with the command "make graph".

generated_files/ - contains the generated files including any json file dumps and
generated verilog and html files.

hardware_modules/ - contains all of the files that define hardware nodes and connections. Non-basic blocks
modules that build on top of basic blocks. Basic blocks are leaf nodes that are all
verilog files. Regular expressions are used to go through the verilog files of the basic
blocks and populate the hardware_library with the appropriate information.

jinja_templates/ - templates for the verilog generation

test_benches/ - test benches for the verilog files. includes a do file for running the test bench from the
command line
"""


"""
The top level is defined by running one of the files within /hardware_modules/non_basic_blocks.
The module that is defined in the top level also recursively defines all the required submodules
that make the module work, all the way down to the leaf nodes, which are called "basic blocks"

/hardware_modules/non_basic_blocks/top_module.py contains the code that shows how to define
a hardware module, its input/output ports, as well as its subgraphs.
"""
with open(
    config["path"] + "/hardware_modules/non_basic_blocks/top_module.py",
    "r",
) as file:
    code = file.read()
    exec(code)

"""
Once the above file is ran, two global libraries are populated. The HardwareLibrary
contains all of the hardware modules that have been defined, along with information
about the inputs, outputs, and internal subgraph within the module. The below function
dumps the json version of the library, which can be viewed in /generated_files/hardware_library.json
"""
hardware_library = HardwareLibrary()
hardware_library.to_json("hardware_library")
"""
The same can be done for ConnectionLibrary, which is a singleton that converts a
user defined json file into a dictionary of custom data structs that would be
passed between nodes in the graph. The json file can be viewed in /generated_files/connection_libary.json
"""
connection_library = ConnectionLibrary()
connection_library.to_json("connection_library")

"""
The file_output_loader library is used to convert all of the modules defined
in the hardware_library to generated verilog files and html files for graph visualization.
"""
file_output_loader.display_hardware_library()

"""
The code below shows how a top level module can be expanded. This expands non-basic blocks
all the way down to the leaf nodes, so that the generated graph is composed of only leaf nodes.
The expanded graph can be found in the generated files folder, in top_module_expanded within
html folder or top_module.sv within the verilog folder.
"""
top = HDLGraph.return_expanded_graph(top_module_name="top_module")
file_output_loader.display_verilog("top_module_expanded", hdl_graph=top)
file_output_loader.generate_verilog("top_module", hdl_graph=top)

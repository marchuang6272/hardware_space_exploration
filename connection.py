import json
from hardware_module import HardwareModule


class Connection:
    def __init__(
        self, source_module, destination_module, source_port, destination_port, key
    ):
        if not verify_ports_exist(
            source_module["hardwareModule"],
            destination_module["hardwareModule"],
            source_port,
            destination_port,
        ):
            raise Exception("Connected ports must exist in the hardware module.")
        elif not verify_connection(
            source_module["hardwareModule"],
            destination_module["hardwareModule"],
            source_port,
            destination_port,
        ):
            raise Exception("Connected ports must have similar type.")
        elif not verify_port_availability(
            source_module["hardwareModule"],
            destination_module["hardwareModule"],
            source_port,
            destination_port,
        ):
            raise Exception("Connections must be available.")
        else:
            source_module["hardwareModule"].add_output_connection(
                port_name=source_port, key=key, connection=self
            )
            destination_module["hardwareModule"].add_input_connection(
                port_name=destination_port, key=key, connection=self
            )
            self.source_port = source_port
            self.destination_port = destination_port
            self.type = source_module["hardwareModule"].output_ports[source_port][
                "type"
            ]


def verify_connection(source_module, destination_module, source_port, destination_port):
    flag = True
    if (
        source_module.output_ports[source_port]["type"]
        != destination_module.input_ports[destination_port]["type"]
    ):
        flag = False
    return flag


def verify_ports_exist(
    source_module, destination_module, source_port, destination_port
):
    flag = True
    if source_port not in source_module.output_ports:
        flag = False
    if destination_port not in destination_module.input_ports:
        flag = False
    return flag


def verify_port_availability(
    source_module, destination_module, source_port, destination_port
):
    flag = True
    if destination_module.input_ports[destination_port]["connection"]:
        flag = False
    return flag

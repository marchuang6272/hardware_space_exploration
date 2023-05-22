#!/usr/bin/env python3

import json
from hardware_module import HardwareModule
from connection import Connection


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Connection) or isinstance(obj, HardwareModule):
            return obj.__dict__
        # Let the base class default method handle the other types
        return json.JSONEncoder.default(self, obj)

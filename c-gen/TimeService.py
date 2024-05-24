import json
import CCodeUtils as ccu
import UserCodeUtils as ucu


class TimeService:
    """Currently, this class handles no implementation-specific information, but this may change eventually"""
    def __init__(self, service: json):
        self.json = service

    def get_file(self) -> ccu.CFile:
        return ccu.CFile("time",
                         "A (user-defined) implementation of the time service",
                         ucu.get_template("time.c"))

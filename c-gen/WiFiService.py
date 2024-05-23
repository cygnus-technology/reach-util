import json
import CCodeUtils as ccu
import UserCodeUtils as ucu


class WiFiService:
    def __init__(self, service: json):
        self.max_access_points = service["maxAccessPoints"]

    def get_file(self) -> ccu.CFile:
        output = ccu.CFile("wifi",
                           "A minimal implementation of Wi-Fi discovery and access",
                           ucu.get_template("wifi.c"))
        output.contents[".c Defines"].append(ccu.CSnippet(f"#define MAX_NUM_WIFI_ACCESS_POINTS {self.max_access_points}"))
        return output
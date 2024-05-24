import json
import CCodeUtils as ccu
import UserCodeUtils as ucu

from CliService import CliService
from CommandService import CommandService
from FileService import FileService
from ParamRepoService import ParamRepoService
from StreamService import StreamService
from TimeService import TimeService
from WiFiService import WiFiService


class ReachDevice:
    class DeviceDescription:
        def __init__(self, spec: json):
            self.name = spec['name']
            self.manufacturer = spec['manufacturer']
            self.description = spec['description']
            self.services = spec['services'].keys()

        def as_struct(self) -> ccu.CStruct:
            service_translation = {
                'parameterRepositoryService': "cr_ServiceIds_PARAMETER_REPO",
                'fileService': "cr_ServiceIds_FILES",
                'commandService': "cr_ServiceIds_COMMANDS",
                'cliService': "cr_ServiceIds_CLI",
                'timeService': "cr_ServiceIds_TIME",
                'wifiService': "cr_ServiceIds_WIFI",
                'streamService': "cr_ServiceIds_STREAMS"
            }
            fields = [{'field': 'device_name', 'value': ccu.CString(self.name)},
                      {'field': 'manufacturer', 'value': ccu.CString(self.manufacturer)},
                      {'field': 'device_description', 'value': ccu.CString(self.description)},
                      {'field': 'services', 'value': ' | '.join([service_translation[svc] for svc in self.services])}]

            return ccu.CStruct(fields, name="const cr_DeviceInfoResponse device_info")

    def __init__(self, device: json):
        self.description = ReachDevice.DeviceDescription(device)
        self.services = {}
        class_map = {'parameterRepositoryService': ParamRepoService,
                     'fileService': FileService,
                     'commandService': CommandService,
                     'cliService': CliService,
                     'timeService': TimeService,
                     'wifiService': WiFiService,
                     'streamService': StreamService}
        for svc in device['services'].keys():
            if svc not in class_map:
                # Unsupported service type
                continue
            else:
                self.services[svc] = class_map[svc](device['services'][svc])

    def get_file(self) -> ccu.CFile:
        output = ccu.CFile("device",
                           "A minimal implementation of device info discovery",
                           ucu.get_template("device.c"))
        output.contents[".c Local/Extern Variables"].append(self.description.as_struct())
        define_map = {'parameterRepositoryService': "PARAMETER",
                      'fileService': "FILE",
                      'commandService': "COMMAND",
                      'cliService': "CLI",
                      'timeService': "TIME",
                      'wifiService': "WIFI",
                      'streamService': "STREAM"}
        for svc in self.services.keys():
            if svc in define_map:
                output.contents['.h Defines'].append(ccu.CSnippet(f"#define INCLUDE_{define_map[svc]}_SERVICE"))
        return output

    def get_all_files(self):
        return [self.get_file()] + [svc.get_file() for svc in self.services.values()]

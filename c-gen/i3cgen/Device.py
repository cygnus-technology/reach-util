import json
from i3cgen.utils import util
from termcolor import colored

def gen_device_info(device: json):
    # build the fields for the device info json
    fields = []
    fields.append({"field": "device_name", "value": f"\"{device['name']}\""})
    fields.append({"field": "manufacturer", "value": f"\"{device['manufacturer']}\""})
    fields.append({"field": "device_description", "value": f"\"{device['description']}\""})
    print(colored('Using hard coded device service IDs in Device.py', 'red'))
    serviceIds = ['PARAMETER_REPO', 'FILES', 'COMMANDS', 'CLI', 'TIME']
    serviceIds = ['cr_ServiceIds_' + sid for sid in serviceIds]
    service_string = " | ".join(serviceIds)
    fields.append({"field": "services", "value": service_string})

    # Place into a struct and format so it may be placed into a c file
    struct = util.gen_protobuf_struct(fields, depth=0)
    struct[0] = f"const cr_DeviceInfoResponse device_info = {struct[0]}"
    struct[-1] += ";"

    output = []
    output.append(struct)

    return output

import json
from i3cgen.utils import util

# From reach.h
# TODO: Make this use the actual reach.h from reach-c-stack to parse these values
service_ids = {'': 'cr_ServiceIds_NO_SVC_ID',
               'parameterRepositoryService': 'cr_ServiceIds_PARAMETER_REPO',
               'fileService': 'cr_ServiceIds_FILES',
               'streamService': 'cr_ServiceIds_STREAMS',
               'commandService': 'cr_ServiceIds_COMMANDS',
               'cliService': 'cr_ServiceIds_CLI',
               'timeService': 'cr_ServiceIds_TIME',
               'WiFService': 'cr_ServiceIds_WIFI'}

def gen_device_info(device: json):
    # build the fields for the device info json
    fields = []
    fields.append({"field": "device_name", "value": f"\"{device['name']}\""})
    fields.append({"field": "manufacturer", "value": f"\"{device['manufacturer']}\""})
    fields.append({"field": "device_description", "value": f"\"{device['description']}\""})

    parsed_ids = []
    for service in device['services']:
        parsed_ids.append(service_ids[service])
    service_string = " | ".join(parsed_ids)
    fields.append({"field": "services", "value": service_string})

    # Place into a struct and format so it may be placed into a c file
    struct = util.gen_protobuf_struct(fields, depth=0)
    struct[0] = f"const cr_DeviceInfoResponse device_info = {struct[0]}"
    struct[-1] += ";"

    output = []
    output.append(struct)

    return output

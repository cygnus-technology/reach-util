import json
from i3cgen.utils import util


class File:
    access_levels = {
        "None": "cr_AccessLevel_NO_ACCESS",
        "Read": "cr_AccessLevel_READ",
        "Write": "cr_AccessLevel_WRITE",
        "Read/Write": "cr_AccessLevel_READ_WRITE"
    }

    storage_locations = {
        "RAM": "cr_StorageLocation_RAM",
        "Extended RAM": "cr_StorageLocation_RAM_EXTENDED",
        "NVM": "cr_StorageLocation_NONVOLATILE",
        "Extended NVM": "cr_StorageLocation_NONVOLATILE_EXTENDED"
    }

    def to_enum(param: json):
        return util.make_c_compatible(f"FILE_{param['name']}", upper=True)

    def to_protobuf(param: json, depth=0):
        fields = [{"field": "file_id", "value": File.to_enum(param)}]
        fields.append({"field": "file_name", "value": f"\"{param['name']}\""})
        fields.append({'field': 'access', 'value': File.access_levels[param['access']]})
        fields.append({'field': 'storage_location', 'value': File.storage_locations[param['storageLocation']]})
        fields.append({'field': 'require_checksum', 'value': param['requireChecksum']})
        if 'maxSize' in param:
            fields.append({'field': 'maximum_size_bytes', 'value': param['maxSize'], 'optional': True})
        return util.gen_protobuf_struct(fields, depth=depth)



def gen_definitions(service: json):
    lines = ["#define INCLUDE_FILE_SERVICE"]
    if service['features']['descriptions']:
        lines.append(f"#define NUM_FILES    {len(service['files'])}")
    return lines

def gen_enums(service: json):
    output = []
    if len(service['files']) > 0:
        enums = []
        values = []
        for file in service['files']:
            enums.append(File.to_enum(file))
            values.append(file['id'])
        output.append(util.gen_enum(enums, values, "file"))
    return output

def gen_variables(service: json):
    output = []
    if len(service['files']) > 0:
        structs = []
        for file in service['files']:
            structs.append(File.to_protobuf(file))
        lines = util.gen_c_array(structs)
        lines[0] = f"cr_FileInfo file_descriptions[NUM_FILES] = {lines[0]}"
        lines[-1] += ';'
        output.append(lines)
    return output

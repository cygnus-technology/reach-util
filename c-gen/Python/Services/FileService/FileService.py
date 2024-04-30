import json
from ... import util

class File:
    def to_enum(param: json):
        return util.make_c_compatible(f"FILE_{param['name']}", upper=True)

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
        output.append(util.gen_enum(enums, values, "files"))
    return output
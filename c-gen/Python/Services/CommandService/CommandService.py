import json
from ... import util

class Command:
    def to_enum(param: json):
        return util.make_c_compatible(f"COMMAND_{param['name']}", upper=True)

def gen_definitions(service: json):
    lines = ["#define INCLUDE_COMMAND_SERVICE"]
    if service['features']['descriptions']:
        lines.append(f"#define NUM_COMMANDS    {len(service['commands'])}")
    return lines

def gen_enums(service: json):
    output = []
    if len(service['commands']) > 0:
        enums = []
        values = []
        for command in service['commands']:
            enums.append(Command.to_enum(command))
            values.append(command['id'])
        output.append(util.gen_enum(enums, values, "command"))
    return output
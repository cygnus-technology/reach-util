import json
from i3cgen.utils import util

class Command:
    def to_enum(param: json):
        return util.make_c_compatible(f"COMMAND_{param['name']}", upper=True)

    def to_protobuf(param: json, depth=0):
        fields = [{'field': 'id', 'value': Command.to_enum(param)}]
        fields.append({'field': 'name', 'value': f"\"{param['description']}\""})

        return util.gen_c_struct(fields, depth=depth)

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

def gen_variables(service: json):
    output = []

    if len(service['commands']) > 0:
        structs = []
        for command in service['commands']:
            structs.append(Command.to_protobuf(command))
        lines = util.gen_c_array(structs)
        lines[0] = f'cr_CommandInfo command_desc[NUM_COMMANDS] = {lines[0]}'
        lines[-1] += ';'
        output.append(lines)

    return output
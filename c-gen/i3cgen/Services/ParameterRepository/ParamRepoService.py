import json
from i3cgen.utils import util
from i3cgen.Services.ParameterRepository import Parameter
from i3cgen.Services.ParameterRepository import ParamExInfo

def gen_definitions(service: json):
    lines = ["#define INCLUDE_PARAMETER_SERVICE"]
    if service['features']['descriptions']:
        if service['parameters']:
            lines.append(f"#define NUM_PARAMS    {len(service['parameters'])}")
        if service['extendedLabels']:
            lines.append(f"#define NUM_EX_PARAMS {len(service['extendedLabels'])}")
    return lines


def gen_enums(service: json):
    # Generate primary parameter enumeration
    # Generate enumeration and bitfield value enumerations
    output = []
    if len(service['parameters']) > 0:
        enums = []
        values = []
        for param in service['parameters']:
            enums.append(Parameter.to_enum(param))
            values.append(param['id'])
        output.append(util.gen_enum(enums, values, "param"))
    if len(service['extendedLabels']) > 0:
        for label in service['extendedLabels']:
            temp = ParamExInfo.to_label_enums(label)
            if temp is not None:
                output.append(temp)
    return output


def gen_variables(service: json):
    output = []
    if len(service['parameters']) > 0:
        structs = []
        for param in service['parameters']:
            structs.append(Parameter.to_protobuf(param))
        lines = util.gen_c_array(structs)
        lines[0] = f"const cr_ParameterInfo param_desc[NUM_PARAMS] = {lines[0]}"
        lines[-1] += ";"
        output.append(lines)
    if len(service['extendedLabels']) > 0:
        for label in service['extendedLabels']:
            output.append(ParamExInfo.to_local_array(label))
        structs = []
        for label in service['extendedLabels']:
            structs.append(ParamExInfo.to_struct(label))
        lines = util.gen_c_array(structs)
        lines[0] = f"const cr_gen_param_ex_t param_ex_desc[NUM_EX_PARAMS] = {lines[0]}"
        lines[-1] += ";"
        output.append(lines)
    return output
import json
from . import Parameter, ParamExInfo
from ... import util


def gen_definitions(service: json):
    lines = ["#define INCLUDE_PARAMETER_SERVICE"]
    if service['features']['descriptions']:
        lines.append(f"#define NUM_PARAMS")
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


# def gen_variables(service: json):
#     output = ["static const "]

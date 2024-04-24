import json
from ... import util

make_c_compatible = util.make_c_compatible
gen_enum = util.gen_enum
gen_c_array = util.gen_c_array
gen_c_struct = util.gen_c_struct


def to_param_ei_enum(pei: json):
    return make_c_compatible(f"PARAM_EI_{pei['name']}", upper=True)


def to_label_enums(pei: json):
    match pei['dataType']:
        case "boolean":
            # No enumeration needed, just true and false
            return None
        case "enumeration":
            # Just one enumeration to generate
            enums = []
            values = []
            for enum in pei['enumValues']:
                enums.append(enum['label'])
                values.append(enum['id'])
            return gen_enum(enums, values, pei['name'], transform_enum_names=True)
        case "bitfield":
            # Generate both the index and the value enumerations
            enums = []
            index_values = []
            bit_values = []
            name = pei['name']
            for enum in pei['bitIndices']:
                enums.append(enum['label'])
                index_values.append(enum['id'])
                temp = make_c_compatible(f"{name} indices {enum['label']}", upper=True)
                bit_values.append(f"0b1 << {temp}")
            output = gen_enum(enums, index_values, f"{name} indices", transform_enum_names=True)
            output.append("")
            output += gen_enum(enums, bit_values, name, transform_enum_names=True)
            return output
        case _:
            raise ValueError(f"Unexpected dataType {pei['dataType']}")


def to_local_array(pei: json, depth=0):
    match pei['dataType']:
        case "boolean":
            elements = [gen_c_struct([{"field": "id", "value": 0},
                                     {"field": "name", "value": f"\"{pei['falseLabel']}\""}], depth=depth),
                        gen_c_struct([{"field": "id", "value": 1},
                                     {"field": "name", "value": f"\"{pei['trueLabel']}\""}], depth=depth)]
        case "enumeration":
            elements = []
            for enum in pei['enumValues']:
                elements.append(gen_c_struct([{"field": "id", "value": enum['id']},
                                             {"field": "name", "value": f"\"{enum['label']}\""}], depth=depth))
        case "bitfield":
            elements = []
            for bit in pei['bitIndices']:
                elements.append(gen_c_struct([{"field": "id", "value": bit['id']},
                                             {"field": "name", "value": f"\"{bit['label']}\""}], depth=depth))
        case _:
            raise ValueError(f"Unexpected dataType {pei['dataType']}")
    output = gen_c_array(elements, 0)
    output[0] = f"static const cr_ParamExKey __cr_gen_pei_{make_c_compatible(pei['name']).lower()}_labels = {output[0]}"
    output[-1] += ";"
    return output


def to_struct(pei: json, depth=0):
    data_types = {
        "boolean": "cr_ParameterDataType_BOOL",
        "enumeration": "cr_ParameterDataType_ENUMERATION",
        "bitfield": "cr_ParameterDataType_BIT_FIELD",
    }

    fields = [{"field": "pei_id", "value": to_param_ei_enum(pei)},
              {"field": "data_type", "value": data_types[pei['dataType']]}]

    match pei['dataType']:
        case "boolean":
            num_labels = 2
        case "enumeration":
            num_labels = len(pei['enumValues'])
        case "bitfield":
            num_labels = len(pei['bitIndices'])
        case _:
            raise ValueError(f"Unexpected dataType {pei['dataType']}")
    fields.append({"field": "num_labels", "value": num_labels})
    fields.append({"field": "labels", "value": f"__cr_gen_pei_{make_c_compatible(pei['name']).lower()}_labels"})
    return gen_c_struct(fields, depth=depth)

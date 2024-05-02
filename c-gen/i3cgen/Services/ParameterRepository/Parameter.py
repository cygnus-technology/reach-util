import json
from i3cgen.utils import util

def to_enum(param: json):
    return util.make_c_compatible(f"PARAM_{param['name']}", upper=True)


def to_protobuf(param: json, depth=0):
    which_desc_types = {
        "uint32": "cr_ParameterDataType_UINT32",
        "int32": "cr_ParameterDataType_INT32",
        "float32": "cr_ParameterDataType_FLOAT32",
        "uint64": "cr_ParameterDataType_UINT64",
        "int64": "cr_ParameterDataType_INT64",
        "float64": "cr_ParameterDataType_FLOAT64",
        "boolean": "cr_ParameterDataType_BOOL",
        "string": "cr_ParameterDataType_STRING",
        "enumeration": "cr_ParameterDataType_ENUMERATION",
        "bitfield": "cr_ParameterDataType_BIT_FIELD",
        "bytearray": "cr_ParameterDataType_BYTE_ARRAY"
    }

    oneof_types = {
        "uint32": "uint32",
        "int32": "int32",
        "float32": "float32",
        "uint64": "uint64",
        "int64": "int64",
        "float64": "float64",
        "boolean": "bool",
        "string": "string",
        "enumeration": "enum",
        "bitfield": "bitfield",
        "bytearray": "bytearray"
    }

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

    fields = [{"field": "id", "value": to_enum(param)}, {"field": "name", "value": f"\"{param['name']}\""}]
    if "description" in param:
        fields.append({"field": "description", "value": f"\"{param['description']}\"", "optional": True})
    fields.append({"field": "access", "value": access_levels[param['access']]})
    fields.append({"field": "storage_location", "value": storage_locations[param['storageLocation']]})
    extra_desc = {"oneOf": "desc", "which": f"{which_desc_types[param['dataType']]} + cr_ParameterInfo_uint32_desc_tag",
                  "field": oneof_types[param['dataType']],
                  "value": []}
    match param['dataType']:
        case x if x in ["uint32", "int32", "uint64", "int64", "float32", "float64", "enumeration"]:
            if 'units' in param:
                extra_desc['value'].append({"field": "units", "optional": True, "value": f"\"{param['units']}\""})
            if 'rangeMin' in param:
                extra_desc['value'].append(
                    {"field": "range_min", "optional": True, "value": param["rangeMin"]})
            if 'defaultValue' in param:
                extra_desc['value'].append(
                    {"field": "default_value", "optional": True, "value": param["defaultValue"]})
            if 'rangeMax' in param:
                extra_desc['value'].append(
                    {"field": "range_max", "optional": True, "value": param["rangeMax"]})
            if x in ["float32", "float64"]:
                if 'precision' in param:
                    extra_desc['value'].append(
                        {"field": "precision", "optional": True, "value": param["precision"]})
            if x == "enumeration":
                if 'labelName' in param:
                    extra_desc['value'].append(
                        {"field": "pei_id", "optional": True,
                         "value": util.make_c_compatible(f"PARAM_EI_{param['labelName']}", upper=True)})
        case "boolean":
            if 'defaultValue' in param:
                extra_desc['value'].append(
                    {"field": "default_value", "optional": True, "value": param["defaultValue"]})
            if 'labelName' in param:
                extra_desc['value'].append({"field": "pei_id", "optional": True,
                                            "value": util.make_c_compatible(f"PARAM_EI_{param['labelName']}", upper=True)})
        case "string":
            if 'defaultValue' in param:
                extra_desc['value'].append(
                    {"field": "default_value", "optional": True, "value": f"\"{param['defaultValue']}\""})
            extra_desc['value'].append({"field": "max_size", "value": param['maxSize']})
        case "bitfield":
            if 'defaultValue' in param:
                extra_desc['value'].append(
                    {"field": "default_value", "optional": True, "value": hex(param['defaultValue'])})
            extra_desc['value'].append(
                {"field": "bits_available", "value": param['bitsAvailable']})
            if 'labelName' in param:
                extra_desc['value'].append({"field": "pei_id", "optional": True,
                                            "value": util.make_c_compatible(f"PARAM_EI_{param['labelName']}", upper=True)})
        case "bytearray":
            if 'defaultValue' in param:
                extra_desc['value'].append(
                    {"field": "default_value", "optional": True, "value": param['defaultValue']})
            extra_desc['value'].append({"field": "max_size", "value": param['maxSize']})
    fields.append(extra_desc)
    return util.gen_protobuf_struct(fields, depth=depth)

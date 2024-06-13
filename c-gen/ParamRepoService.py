import json
import CCodeUtils as ccu
import UserCodeUtils as ucu


class ParamRepoService:
    class Parameter:
        def __init__(self, param: json):
            self.json = param
            self.has_default_notifications = ("defaultNotifications" in self.json)

        def as_enum(self) -> str:
            return ccu.make_c_compatible(f"PARAM_{self.json['name']}", upper=True)

        def as_protobuf(self) -> ccu.CStruct:
            oneof_types = {
                "uint32": "uint32_desc",
                "int32": "int32_desc",
                "float32": "float32_desc",
                "uint64": "uint64_desc",
                "int64": "int64_desc",
                "float64": "float64_desc",
                "boolean": "bool_desc",
                "string": "string_desc",
                "enumeration": "enum_desc",
                "bitfield": "bitfield_desc",
                "bytearray": "bytearray_desc"
            }
            fields = [{"field": "id", "value": self.as_enum()},
                      {"field": "name", "value": ccu.CString(self.json['name'])}]
            if "description" in self.json:
                fields.append({"field": "description",
                               "value": ccu.CString(self.json['description']), "optional": True})
            fields.append({"field": "access", "value": ccu.get_access_enum(self.json['access'])})
            fields.append({"field": "storage_location",
                           "value": ccu.get_storage_location_enum(self.json['storageLocation'])})
            extra_desc = {"oneOf": "desc",
                          "which":
                              f"{ccu.get_param_type_enum(self.json['dataType'])} + cr_ParameterInfo_uint32_desc_tag",
                          "field": oneof_types[self.json['dataType']],
                          "value": []}
            match self.json['dataType']:
                case x if x in ["uint32", "int32", "uint64", "int64", "float32", "float64", "enumeration"]:
                    if 'units' in self.json:
                        extra_desc['value'].append(
                            {"field": "units", "optional": True, "value": ccu.CString(self.json['units'])})
                    if 'rangeMin' in self.json:
                        extra_desc['value'].append(
                            {"field": "range_min", "optional": True, "value": self.json["rangeMin"]})
                    if 'defaultValue' in self.json:
                        extra_desc['value'].append(
                            {"field": "default_value", "optional": True, "value": self.json["defaultValue"]})
                    if 'rangeMax' in self.json:
                        extra_desc['value'].append(
                            {"field": "range_max", "optional": True, "value": self.json["rangeMax"]})
                    if x in ["float32", "float64"]:
                        if 'precision' in self.json:
                            extra_desc['value'].append(
                                {"field": "precision", "optional": True, "value": self.json["precision"]})
                    if x == "enumeration":
                        if 'labelName' in self.json:
                            extra_desc['value'].append(
                                {"field": "pei_id", "optional": True,
                                 "value": ccu.make_c_compatible(f"PARAM_EI_{self.json['labelName']}", upper=True)})
                case "boolean":
                    if 'defaultValue' in self.json:
                        extra_desc['value'].append(
                            {"field": "default_value", "optional": True, "value": ccu.CBool(self.json["defaultValue"])})
                    if 'labelName' in self.json:
                        extra_desc['value'].append({"field": "pei_id", "optional": True,
                                                    "value": ccu.make_c_compatible(f"PARAM_EI_{self.json['labelName']}",
                                                                                   upper=True)})
                case "string":
                    if 'defaultValue' in self.json:
                        extra_desc['value'].append(
                            {"field": "default_value", "optional": True,
                             "value": ccu.CString(self.json['defaultValue'])})
                    extra_desc['value'].append({"field": "max_size", "value": self.json['maxSize']})
                case "bitfield":
                    if 'defaultValue' in self.json:
                        extra_desc['value'].append(
                            {"field": "default_value", "optional": True, "value": hex(self.json['defaultValue'])})
                    extra_desc['value'].append(
                        {"field": "bits_available", "value": self.json['bitsAvailable']})
                    if 'labelName' in self.json:
                        extra_desc['value'].append({"field": "pei_id", "optional": True,
                                                    "value": ccu.make_c_compatible(f"PARAM_EI_{self.json['labelName']}",
                                                                                   upper=True)})
                case "bytearray":
                    if 'defaultValue' in self.json:
                        extra_desc['value'].append(
                            {"field": "default_value", "optional": True, "value": self.json['defaultValue']})
                    extra_desc['value'].append({"field": "max_size", "value": self.json['maxSize']})
            fields.append(extra_desc)
            return ccu.CStruct(fields, is_protobuf=True)

        def as_notify_init_struct(self):
            if not self.has_default_notifications:
                return None
            else:
                fields = [{"field": "parameter_id", "value": self.as_enum()}]
                if "minInterval" in self.json["defaultNotifications"]:
                    fields.append({"field": "minimum_notification_period",
                                   "value": self.json["defaultNotifications"]["minInterval"]})
                if "maxInterval" in self.json["defaultNotifications"]:
                    fields.append({"field": "maximum_notification_period",
                                   "value": self.json["defaultNotifications"]["maxInterval"]})
                if "minDelta" in self.json["defaultNotifications"]:
                    fields.append({"field": "minimum_delta",
                                   "value": self.json["defaultNotifications"]["minDelta"]})
                return ccu.CStruct(fields)

    class ExtendedLabel:
        def __init__(self, label: json):
            self.json = label

        def as_enum(self):
            return ccu.make_c_compatible(f"PARAM_EI_{self.json['name']}", upper=True)

        def as_label_enums(self):
            match self.json['dataType']:
                case "boolean":
                    # Booleans don't need a special enumeration
                    return []
                case "enumeration":
                    # Just one enumeration to generate
                    enums = [x['label'] for x in self.json["enumValues"]]
                    values = [x.get("id", None) for x in self.json["enumValues"]]
                    return [ccu.CEnum(enums, values, self.json['name'], transform_enum_names=True)]
                case "bitfield":
                    # Generate both the index and the value enumerations
                    enums = [x['label'] for x in self.json['bitIndices']]
                    index_values = [x.get("id", None) for x in self.json['bitIndices']]
                    name = self.json['name']
                    bit_values = [f"""(0b1 << {ccu.make_c_compatible(f"{name} indices {x['label']}", upper=True)})"""
                                  for x in self.json['bitIndices']]
                    return [ccu.CEnum(enums, index_values, f"{name} indices", transform_enum_names=True),
                            ccu.CEnum(enums, bit_values, name, transform_enum_names=True)]

        def as_local_key_array(self):
            match self.json['dataType']:
                case "boolean":
                    elements = [ccu.CStruct([{"field": "id", "value": 0},
                                             {"field": "name", "value": ccu.CString(self.json['falseLabel'])}]),
                                ccu.CStruct([{"field": "id", "value": 1},
                                             {"field": "name", "value": ccu.CString(self.json['trueLabel'])}])]
                case "enumeration":
                    elements = []
                    for enum in self.json['enumValues']:
                        elements.append(ccu.CStruct([{"field": "id",
                                                      "value": ccu.make_c_compatible(
                                                          f"{self.json['name']} {enum['label']}", upper=True)},
                                                     {"field": "name", "value": f"\"{enum['label']}\""}]))
                case "bitfield":
                    elements = []
                    for bit in self.json['bitIndices']:
                        elements.append(ccu.CStruct([{"field": "id",
                                                      "value": ccu.make_c_compatible(
                                                          f"{self.json['name']} indices {bit['label']}", upper=True)},
                                                     {"field": "name", "value": f"\"{bit['label']}\""}]))
                case _:
                    raise ValueError(f"Unexpected dataType {self.json['dataType']}")
            return ccu.CArray(elements,
                              name=f"static const cr_ParamExKey __cr_gen_pei_"
                                   f"{ccu.make_c_compatible(self.json['name']).lower()}_labels")

        def as_struct(self):
            fields = [{"field": "pei_id", "value": self.as_enum()},
                      {"field": "data_type", "value": ccu.get_param_type_enum(self.json['dataType'])}]

            match self.json['dataType']:
                case "boolean":
                    num_labels = 2
                case "enumeration":
                    num_labels = len(self.json['enumValues'])
                case "bitfield":
                    num_labels = len(self.json['bitIndices'])
                case _:
                    raise ValueError(f"Unexpected dataType {self.json['dataType']}")
            fields.append({"field": "num_labels", "value": num_labels})
            fields.append(
                {"field": "labels",
                 "value": f"__cr_gen_pei_{ccu.make_c_compatible(self.json['name']).lower()}_labels"})
            return ccu.CStruct(fields)

    def __init__(self, service: json):
        self.parameters = [ParamRepoService.Parameter(param) for param in service.get("parameters", [])]
        self.labels = [ParamRepoService.ExtendedLabel(label) for label in service.get("extendedLabels", [])]

    def get_file(self):
        sub_files = []
        if self.parameters:
            enums = [ccu.CEnum([x.as_enum() for x in self.parameters],
                               [x.json.get("id", None) for x in self.parameters], "param")]
            param_desc_structs = [x.as_protobuf() for x in self.parameters]
            default_notification_structs = [x.as_notify_init_struct()
                                            for x in self.parameters if x.has_default_notifications]
            sub_files.append(ccu.CFile("pr_parameters", "", ucu.get_template("pr_parameters.c")))
            sub_files[-1].contents[".h Defines"].append(ccu.CSnippet(f"#define NUM_PARAMS {len(self.parameters)}"))
            sub_files[-1].contents[".h Data Types"] += enums
            sub_files[-1].contents[".c Local/Extern Variables"].append(
                ccu.CArray(param_desc_structs, name="static const cr_ParameterInfo param_desc"))
            if default_notification_structs:
                sub_files.append(ccu.CFile("pr_default_notifications", "",
                                           ucu.get_template("pr_default_notifications.c")))
                sub_files[-1].contents[".h Defines"].append(
                    ccu.CSnippet(f"#define NUM_INIT_PARAMETER_NOTIFICATIONS {len(default_notification_structs)}"))
                sub_files[-1].contents[".c Local/Extern Variables"].append(
                    ccu.CArray(default_notification_structs, name="static cr_ParameterNotifyConfig sParamNotifyInit"))

        if self.labels:
            typedefs = [ccu.CEnum([x.as_enum() for x in self.labels],
                                  [x.json.get("id", None) for x in self.labels], "param_ei")]
            typedefs += [x for y in self.labels for x in y.as_label_enums()]
            arrays = [x.as_local_key_array() for x in self.labels]
            arrays.append(
                ccu.CArray([x.as_struct() for x in self.labels], name="static const cr_gen_param_ex_t param_ex_desc"))
            sub_files.append(ccu.CFile("pr_labels", "", ucu.get_template("pr_labels.c")))
            sub_files[-1].contents[".h Defines"].append(ccu.CSnippet(f"#define NUM_EX_PARAMS {len(self.labels)}"))
            sub_files[-1].contents[".h Data Types"] += typedefs
            sub_files[-1].contents[".c Local/Extern Variables"] += arrays
        return ccu.CFile.combine(sub_files, "parameters", "A minimal implementation of Reach data access.")

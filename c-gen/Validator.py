from pathlib import Path
import json

import jsonschema.exceptions
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012
from jsonschema import Draft202012Validator as Validator


class DeviceDescriptionValidator:
    def __init__(self, path: str):
        elements = []
        root = None
        for file in Path(path).iterdir():
            f = open(file)
            # print(f"{file}")
            json_data = json.load(f)
            if file.name == "reachDevice.json":
                root = json_data
                continue
            schema = Resource(contents=json_data, specification=DRAFT202012)
            elem = (json_data['$id'], schema)
            elements.append(elem)
            f.close()
        registry = Registry().with_resources(elements)
        self.validator = Validator(root, registry=registry)

    def validate(self, d: json):
        def update_name_id_list(j: json, desc: str, id_key='id', name_key='name', max_value=0xFFFFFFFF):
            current_id = 0
            names = []
            local_error_found = False
            for i in range(len(j)):
                if id_key in j[i]:
                    # Check that manually-set IDs do not result in ID collisions
                    if current_id >= j[i][id_key]:
                        errors.append(
                            f"ID {j[i][id_key]} for {desc.lower()} '{j[i][name_key]}' has already been used")
                        local_error_found = True
                        break
                    current_id = j[i][id_key]
                if current_id > max_value:
                    errors.append(
                        f"{desc} '{j[i][name_key]}' has an ID greater than the supported limit of {max_value}")
                    local_error_found = True
                    break
                current_id += 1
                if j[i][name_key] in names:
                    errors.append(
                        f"The name '{j[i][name_key]}' for the {desc.lower()} at index {i} has already been used")
                    local_error_found = True
                    break
            if local_error_found:
                return None
            return j

        # Validate against the schema, which will ensure that the JSON is generally formatted correctly
        self.validator.validate(d)
        errors = []

        # Some validation is too complicated to easily do with JSON schema
        # Parameter repository validation
        if 'parameterRepositoryService' in d['services']:
            # Parameter extended label validation
            if 'extendedLabels' in d['services']['parameterRepositoryService']:
                # Assign and verify IDs, as well as making sure names don't conflict
                new_labels = update_name_id_list(
                    d['services']['parameterRepositoryService']['extendedLabels'],
                    "Extended label")
                if new_labels is not None:
                    # Assign and verify enum/bitfield values, as well as making sure names don't conflict
                    for label in new_labels:
                        match label['dataType']:
                            case 'enumeration':
                                label['enumValues'] = update_name_id_list(
                                    label['enumValues'], f"{label['name']} enumeration label", name_key='label')
                            case 'bitfield':
                                label['bitIndices'] = update_name_id_list(
                                    label['bitIndices'], f"{label['name']} bitfield label",
                                    name_key='label', max_value=63)
                    d['services']['parameterRepositoryService']['extendedLabels'] = new_labels

            # Parameter description validation
            if 'parameters' in d['services']['parameterRepositoryService']:
                # Assign and verify IDs, as well as making sure names don't conflict
                new_parameter_descriptions = update_name_id_list(
                    d['services']['parameterRepositoryService']['parameters'],
                    "Parameter")
                if new_parameter_descriptions is not None:
                    d['services']['parameterRepositoryService']['parameters'] = new_parameter_descriptions
                    for param in d['services']['parameterRepositoryService']['parameters']:
                        if 'labelName' in param:
                            # Verify that referenced labels actually exist
                            found = False
                            for label_set in d['services']['parameterRepositoryService']['extendedLabels']:
                                if label_set['name'] == param['labelName']:
                                    found = True
                                    break
                            if not found:
                                errors.append(f"Extended label '{param['labelName']}' was not defined")
                                continue
                        if "rangeMin" in param and "rangeMax" in param:
                            # Verify that minimum and maximum values make sense
                            if param["rangeMax"] < param["rangeMin"]:
                                errors.append(f"Parameter '{param['name']}' has a maximum value ({param['rangeMax']}) "
                                              f"which is smaller than its minimum value ({param['rangeMin']})")
                                continue
                        if "defaultValue" in param:
                            # Make sure that default values are possible within the other constraints which were defined
                            if param["dataType"] in ["uint32", "uint64", "int32", "int64",
                                                     "float32", "float64", "enumeration"]:
                                if "rangeMin" in param and param["defaultValue"] < param["rangeMin"]:
                                    errors.append(f"Parameter '{param['name']}' has a default value "
                                                  f"({param['defaultValue']}) which is smaller than its minimum value "
                                                  f"({param['rangeMin']})")
                                    continue
                                if "rangeMax" in param and param["defaultValue"] > param["rangeMax"]:
                                    errors.append(f"Parameter '{param['name']}' has a default value "
                                                  f"({param['defaultValue']}) which is larger than its maximum value "
                                                  f"({param['rangeMax']})")
                                    continue
                            elif param["dataType"] == "bitfield":
                                if param["defaultValue"] > 2 ** param["bitsAvailable"]:
                                    errors.append(f"Parameter '{param['name']}' has a default value "
                                                  f"({param['defaultValue']}) which is larger than fits in "
                                                  f"{param['bitsAvailable']} bits")
                                    continue
                            elif param["dataType"] in ["string", "bytearray"]:
                                if len(param["defaultValue"]) > param["maxSize"]:
                                    errors.append(f"Parameter '{param['name']}' has a default value "
                                                  f"({param['defaultValue']}) which is longer than fits in "
                                                  f"{param['maxSize']} bytes")
                                    continue

        # File list validation
        if 'files' in d['services'].get('fileService', []):
            # Assign and verify IDs, as well as making sure names don't conflict
            new_files = update_name_id_list(
                d['services']['fileService']['files'],
                "File")
            if new_files is not None:
                d['services']['fileService']['files'] = new_files

        # Command list validation
        if 'commands' in d['services'].get('commandService', []):
            # Assign and verify IDs, as well as making sure names don't conflict
            new_commands = update_name_id_list(
                d['services']['commandService']['commands'],
                "Command")
            if new_commands is not None:
                d['services']['commandService']['commands'] = new_commands

        # CLI command validation
        if 'commands' in d['services'].get('cliService', []):
            command_strings = []
            for command in d['services']['cliService']['commands']:
                if command['string'] in command_strings:
                    errors.append(f"CLI command '{command['string']}' appears more than once")

        if errors:
            errors = "\n".join(errors)
            raise Exception(f"Failed to validate file, encountered the following errors:\n{errors}")
        return d

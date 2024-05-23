import json
import CCodeUtils as ccu
import UserCodeUtils as ucu


class CommandService:
    class Command:
        def __init__(self, cmd: json):
            self.name = cmd['name']
            self.id = cmd.get('id', None)
            self.description = cmd.get('description', None)
            self.timeout = cmd.get('timeout', None)

        def as_enum(self) -> str:
            return ccu.make_c_compatible(f"COMMAND_{self.name}", upper=True)

        def as_struct(self) -> ccu.CStruct:
            fields = [{'field': 'id', 'value': self.as_enum()},
                      {'field': 'name', 'value': ccu.CString(self.name)}]
            if self.description:
                fields.append({'field': 'description', 'value': ccu.CString(self.description), 'optional': True})
            if self.timeout:
                fields.append({'field': 'timeout', 'value': self.timeout, 'optional': True})
            return ccu.CStruct(fields, is_protobuf=True)

    def __init__(self, service: json):
        self.commands = [CommandService.Command(cmd) for cmd in service['commands']]

    def get_file(self) -> ccu.CFile:
        output = ccu.CFile("commands",
                           "A minimal implementation of command discovery and handling",
                           ucu.get_template("commands.c"))
        enums = [ccu.CEnum([x.as_enum() for x in self.commands], [x.id for x in self.commands], "command")]
        descriptions = [cmd.as_struct() for cmd in self.commands]
        output.contents[".h Defines"].append(ccu.CSnippet(f"#define NUM_COMMANDS {len(self.commands)}"))
        output.contents[".h Data Types"] += enums
        output.contents[".c Local/Extern Variables"].append(
            ccu.CArray(descriptions, name="static const cr_CommandInfo command_desc"))
        return output

# with open("../reach-silabs/Reach_silabs.json", "r") as f:
#     test = json.load(f)
# import Validator
# validator = Validator.DeviceDescriptionValidator("schemas")
# test = validator.validate(test)
#
# test_pr = CommandService(test["services"]["commandService"])
#
# test_file = test_pr.get_file()
# print(test_file.gen_c_file())
import re

import ScriptVersion

HEADER_WIDTH = 93

indent = "    "


def config(new_indent: str):
    """Used to set the standard indent for all generated files"""
    global indent
    indent = new_indent


def make_c_compatible(name: str, upper=False) -> str:
    """Used to convert strings to valid C identifiers"""
    if upper:
        name = name.upper()
    else:
        name = name.lower()
    return re.sub(r'\W+|^(?=\d)', '_', name).removesuffix("_")


def get_param_type_enum(param_type: str):
    value_map = {
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
    if param_type not in value_map.keys():
        raise ValueError(f"Programming/JSON error: {param_type} is not a supported parameter type")
    return value_map[param_type]


def get_access_enum(access: str):
    value_map = {
        "None": "cr_AccessLevel_NO_ACCESS",
        "Read": "cr_AccessLevel_READ",
        "Write": "cr_AccessLevel_WRITE",
        "Read/Write": "cr_AccessLevel_READ_WRITE"
    }
    if access not in value_map.keys():
        raise ValueError(f"Programming/JSON error: {access} is not a supported access option")
    return value_map[access]


def get_storage_location_enum(location: str):
    value_map = {
        "RAM": "cr_StorageLocation_RAM",
        "Extended RAM": "cr_StorageLocation_RAM_EXTENDED",
        "NVM": "cr_StorageLocation_NONVOLATILE",
        "Extended NVM": "cr_StorageLocation_NONVOLATILE_EXTENDED"
    }
    if location not in value_map.keys():
        raise ValueError(f"Programming/JSON error: {location} is not a supported storage location")
    return value_map[location]


class CBool:
    def __init__(self, val: bool):
        self.val = val

    def __repr__(self):
        if self.val:
            return "true"
        else:
            return "false"


class CString:
    def __init__(self, text: str):
        self.text = text

    def __repr__(self):
        # Replace special characters with their C string representations
        replacement_map = [
            ["\r", r"\r"],
            ["\n", r"\n"],
            ["\t", r"\t"],
            ["°", r"\xC2\xB0"],
        ]
        out = self.text
        for repl in replacement_map:
            out = out.replace(repl[0], repl[1])
        return f'"{out}"'


class CSnippet:
    def __init__(self, text: str | list):
        if type(text) is str:
            self.code = [text]
        else:
            self.code = text

    def crepr(self, depth=0, leading_indent=True):
        output = []
        for line in self.code:
            modified_line = line.replace('\t', indent)
            output.append(f"{indent * depth}{modified_line}")
        if not leading_indent:
            output[0] = output[0].lstrip()
        return "\n".join(output)


class CInclude:
    def __init__(self, raw: str = None, name: str = None, system=False):
        if raw:
            temp = raw.removeprefix("#include").strip()
            if "<" in temp:
                self.system = True
                self.name = temp.strip("<>")
            else:
                self.system = False
                self.name = temp.strip('"')
        else:
            if not name:
                raise ValueError("No include name found")
            self.name = name
            self.system = system

    def crepr(self, depth=0):
        if self.system:
            return f"#include <{self.name}>"
        else:
            return f'{indent * depth}#include "{self.name}"'

    def __repr__(self):
        return self.crepr()

    def __eq__(self, other):
        if type(other) is CInclude:
            return self.name == other.name
        else:
            return self.name == other

    def __gt__(self, other):
        if type(other) is CInclude:
            if self.system != other.system:
                return other.system
            else:
                return self.name > other.name
        else:
            return self.name > other


class CVariable:
    def __init__(self, raw: str = None, name: str = None, value: str = None):
        if raw:
            if "=" in raw:
                temp = raw.strip(";").split("=")
                self.name = temp[0].strip()
                self.value = temp[1].strip()
            else:
                self.name = raw.strip(";")
                self.value = None
        else:
            if not name:
                raise ValueError("Variables must have a name in this current implementation")
            self.name = name
            self.value = value

    def crepr(self, depth=0, extern=False):
        if extern:
            return f"{indent * depth}extern {self.name};"
        else:
            if self.value:
                return f"{indent * depth}{self.name} = {self.value};"
            else:
                return f"{indent * depth}{self.name};"

    def __repr__(self):
        return self.crepr()


class CEnum:
    def __init__(self, enums, values, name, transform_enum_names=False):
        if transform_enum_names:
            transformed_enums = []
            for enum in enums:
                raw_enum = f"{name} {enum}"
                transformed_enums.append(make_c_compatible(raw_enum, upper=True))
        else:
            transformed_enums = enums.copy()
        self.code = [f"typedef enum {{"]
        max_len = len(max(transformed_enums, key=len))
        for enum, val in zip(transformed_enums, values):
            if val is not None:
                self.code.append(f"{indent}{enum.ljust(max_len)} = {val},")
            else:
                self.code.append(f"{indent}{enum},")
        self.code.append(f"}} {make_c_compatible(f'{name}_t')};")

    def crepr(self, depth=0, leading_indent=True):
        output = []
        for line in self.code:
            modified_line = line.replace('\t', indent)
            output.append(f"{indent * depth}{modified_line}")
        if not leading_indent:
            output[0] = output[0].lstrip()
        return "\n".join(output)


class CStruct:
    def __init__(self, elements, name=None, is_protobuf=False):
        self.name = name
        self.elements = elements
        self.is_protobuf = is_protobuf

    def crepr(self, depth=0, leading_indent=True, outer=False, extern=False):
        if outer and extern:
            output = f"{indent * depth}extern {self.name};"
            if not leading_indent:
                output.strip()
            return output
        if self.is_protobuf:
            raw_elements = []
            for elem in self.elements:
                if "oneOf" in elem:
                    if "which" in elem:
                        raw_elements.append({"field": f"which_{elem['oneOf']}", "value": f"{elem['which']}"})
                    else:
                        raw_elements.append({"field": f"which_{elem['oneOf']}", "value": f"{elem['field']}"})
                    for el in elem['value']:
                        if "optional" in el and el["optional"]:
                            raw_elements.append(
                                {"field": f"{elem['oneOf']}.{elem['field']}.has_{el['field']}", "value": CBool(True)})
                        raw_elements.append(
                            {"field": f"{elem['oneOf']}.{elem['field']}.{el['field']}", "value": el['value']})
                elif "optional" in elem and elem["optional"]:
                    raw_elements.append({"field": f"has_{elem['field']}", "value": CBool(True)})
                    raw_elements.append({"field": elem['field'], "value": elem['value']})
                else:
                    raw_elements.append({"field": elem['field'], "value": elem['value']})
        else:
            raw_elements = self.elements.copy()
        if self.name:
            output = [f"{indent * depth}{self.name} = {{"]
        else:
            output = [f"{indent * depth}{{"]
        for elem in raw_elements:
            field = elem["field"]
            val = elem["value"]
            if type(val) in [CSnippet, CVariable, CArray, CStruct]:
                output.append(f"{indent * (depth + 1)}.{field} = {val.crepr(depth + 1, leading_indent=False)},")
            else:
                output.append(f"{indent * (depth + 1)}.{field} = {val},")
        # Remove the last comma, which is unneeded
        output[-1] = output[-1][:-1]
        output.append(f"{indent * depth}}}")
        if outer:
            output[-1] += ";"
        if not leading_indent:
            output[0] = output[0].lstrip()
        return "\n".join(output)


class CArray:
    def __init__(self, elements, name=None):
        self.elements = elements
        self.name = name

    def crepr(self, depth=0, leading_indent=True, outer=False, extern=False):
        if outer and extern:
            output = f"{indent * depth}extern {self.name}[{len(self.elements)}];"
            if not leading_indent:
                output.strip()
            return output
        if self.name:
            output = [f"{indent * depth}{self.name}[] = {{"]
        else:
            output = [f"{indent * depth}{{"]
        for elem in self.elements:
            if type(elem) in [CSnippet, CVariable, CArray, CStruct]:
                output.append(f"{indent * (depth + 1)}{elem.crepr(depth + 1, leading_indent=False)},")
            else:
                output.append(f"{indent * (depth + 1)}{elem},")
        # Remove the last comma, which is unneeded
        output[-1] = output[-1][:-1]
        output.append(f"{indent * depth}}}")
        if outer:
            output[-1] += ";"
        if not leading_indent:
            output[0] = output[0].lstrip()
        return "\n".join(output)


class CFunction:
    def __init__(self, raw: str = None, comment: str = None, decl: str = None, body: str = None):
        if raw:
            pattern = r'(.*)\n?\{\n?([\S\s]*)\}'
            match = re.search(pattern, raw)
            # If there's no blank line between the start of the function and the other content, assume it's a doc comment
            if match.start() > 1 and not (raw[match.start() - 1] == raw[match.start() - 2] == "\n"):
                self.comment = raw[:match.start()].strip()
            else:
                self.comment = None
            self.decl = match.groups()[0]
            self.body = match.groups()[1].strip("\n")
        else:
            self.comment = comment
            self.decl = decl
            self.body = body

    def crepr(self, decl_only=False):
        if decl_only:
            # Include the declaration and doc comment, but not the body
            output = f"{self.decl};"
            if self.comment:
                output = f"\n{self.comment}\n" + output
            return output
        else:
            return f"{self.decl}\n{{\n{self.body}\n}}"


class CFile:
    @staticmethod
    def gen_header(brief: str):
        return r'''/********************************************************************************************
 *    _ ____  ___             _         _     ___              _                        _
 *   (_)__ / | _ \_ _ ___  __| |_  _ __| |_  |   \ _____ _____| |___ _ __ _ __  ___ _ _| |_
 *   | ||_ \ |  _/ '_/ _ \/ _` | || / _|  _| | |) / -_) V / -_) / _ \ '_ \ '  \/ -_) ' \  _|
 *   |_|___/ |_| |_| \___/\__,_|\_,_\__|\__| |___/\___|\_/\___|_\___/ .__/_|_|_\___|_||_\__|
 *                                                                  |_|
 *                           -----------------------------------
 *                          Copyright i3 Product Development 2024
 *
 * MIT License
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 * \brief ''' + f"{brief}" + r'''
 *
 * Original Author: Chuck Peplinski
 * Script Author: Joseph Peplinski
 *
 * Generated with version ''' + \
        f"{ScriptVersion.SCRIPT_VERSION}" + ''' of the C code generator
 *
 ********************************************************************************************/'''

    @staticmethod
    def gen_code_section_header(section: str, lightweight=False):
        if lightweight:
            return f"// {section}\n"
        else:
            centered_text = f"{section:^{len(section) + 10}}"
            asterisk_width = (HEADER_WIDTH - len(centered_text)) / 2
            if asterisk_width % 2 == 1:
                left = int(asterisk_width)
                right = int(asterisk_width) + 1
            else:
                left = right = int(asterisk_width)
            return f"/{'*' * (HEADER_WIDTH - 1)}\n {'*' * (left - 1)}{centered_text}{'*' * right}\n {'*' * (HEADER_WIDTH - 2)}/\n"

    @staticmethod
    def gen_user_code_section(filename: str, section: str):
        label = f"{filename}: User {section}"
        return f"/* User code start [{label}] */\n/* User code end [{label}] */\n"

    @classmethod
    def combine(cls, files: list, new_filename: str, new_brief: str):
        new_contents = {}
        for file in files:
            for key in file.contents.keys():
                if key in new_contents.keys():
                    new_contents[key] += file.contents[key]
                else:
                    new_contents[key] = file.contents[key]
        return CFile(new_filename, new_brief, new_contents)

    @staticmethod
    def optimize_imports(imports: list) -> list:
        new_imports = []
        for i in imports:
            if type(i) != CInclude:
                # Currently not supporting ifdefs and such in include blocks
                # Assume these are blank lines
                continue
            elif i in new_imports:
                # System imports take priority
                if i.system:
                    new_imports[new_imports.index(i)].system = True
            else:
                new_imports.append(i)
        new_imports.sort()
        return new_imports

    def __init__(self, filename: str, brief: str, template: str | dict):
        def gather_template_code(t: str) -> dict:
            def find_functions(block: str) -> list:
                end_positions = []
                # Regex to find the end of functions, assuming some formatting requirements
                p = r'^}'
                for m in re.finditer(p, block, flags=re.MULTILINE):
                    end_positions.append(m.start() + 1)
                match len(end_positions):
                    case 0:
                        return []
                    case 1:
                        return [CFunction(block)]
                    case _:
                        end_positions.insert(0, 0)
                        return [CFunction(block[i:j].strip()) for i, j in
                                zip(end_positions, end_positions[1:] + [None])][:-1]

            pattern = r"\/\* Template code start \[(.+)\] \*\/([\S\s]*)\n\/\* Template code end \[\1\] \*\/"
            # Find the template code blocks
            matches = re.findall(pattern, t)
            template_code = {}
            for code in matches:
                n = code[0]
                c = code[1]
                if n in template_code.keys() or "Template code start [" in code[1]:
                    raise ValueError(f"Found reused template code block name \"{n}\"")
                if c == "":
                    template_code[n] = []
                else:
                    # Store the user code associated with the user code block's label
                    if "Includes" in n:
                        lines = [x for x in c.split('\n') if x]
                        imports = []
                        for line in lines:
                            include = CInclude(raw=line)
                            if include not in imports:
                                imports.append(include)
                        template_code[n] = imports
                    elif "Variables" in n:
                        temp = [x for x in c.split("\n") if x]
                        variables = []
                        for var in temp:
                            variables.append(CVariable(raw=var))
                        template_code[n] = variables
                    elif "Functions" in n:
                        template_code[n] = find_functions(c)
                    else:
                        # No complicated parsing required here
                        temp = c.strip(' \n')
                        if temp:
                            template_code[n] = [CSnippet(temp.split("\n"))]
                        else:
                            template_code[n] = []
            return template_code

        self.filename = filename
        self.brief = brief
        if type(template) is str:
            self.contents = gather_template_code(template)
        else:
            self.contents = template

    def h_file_needed(self):
        for key in self.contents.keys():
            if key[:3] != ".h ":
                continue
            if self.contents[key]:
                return True
        return False

    def gen_h_file(self):
        if not self.h_file_needed():
            return None
        guard_define = f"_{self.filename.upper()}_H_"
        output = f"{self.gen_header(self.brief)}\n\n#ifndef {guard_define}\n#define {guard_define}\n\n"

        # Clean up the imports
        self.contents[".h Includes"] = self.optimize_imports(self.contents[".h Includes"])

        for key in self.contents.keys():
            if key[:3] != ".h ":
                continue
            output += f"{self.gen_code_section_header(key[3:], lightweight=True)}\n"
            if self.contents[key]:
                for elem in self.contents[key]:
                    if type(elem) in [CVariable, CArray, CStruct]:
                        output += f"{elem.crepr(extern=True)}"
                    elif type(elem) is CFunction:
                        output += f"{elem.crepr(decl_only=True)}"
                    else:
                        output += f"{elem.crepr()}"
                    output += "\n"
            output += self.gen_user_code_section(self.filename + ".h", key[3:])
        output += f"\n#endif // {guard_define}"
        return output

    def gen_c_file(self):
        output = f"{self.gen_header(self.brief)}\n\n"

        # Clean up the imports:
        self.contents[".c Includes"] = self.optimize_imports(self.contents[".c Includes"])
        # Messy solution: duplicate the local function key
        temp_contents = {}
        for key in self.contents.keys():
            temp_contents[key] = self.contents[key]
            if key == ".c Local/Extern Variables":
                temp_contents[".c Local Function Declarations"] = self.contents[".c Local Functions"]
        if self.h_file_needed():
            if f"{self.filename}.h" in self.contents[".c Includes"]:
                self.contents[".c Includes"].remove(f"{self.filename}.h")
            self.contents[".c Includes"].insert(0, CInclude(name=f"{self.filename}.h"))
        for key in temp_contents.keys():
            if key[:3] != ".c " and "Variables" not in key and "Functions" not in key:
                continue

            output += f"{self.gen_code_section_header(key[3:])}\n"
            if temp_contents[key]:
                if "Function Declarations" in key:
                    # Special handling for these declarations
                    for elem in temp_contents[key]:
                        output += f"{elem.crepr(decl_only=True)}\n"
                else:
                    for elem in temp_contents[key]:
                        if type(elem) in [CArray, CStruct]:
                            output += f"{elem.crepr(outer=True)}\n"
                        else:
                            output += f"{elem.crepr()}\n"
                        if type(elem) in [CArray, CStruct, CFunction]:
                            output += "\n"
                # Ensure there is one empty line between template code and the user code block
                output = output.rstrip("\n")
                output += "\n\n"
            output += self.gen_user_code_section(self.filename + ".c", key[3:])
            output += "\n"

        return output

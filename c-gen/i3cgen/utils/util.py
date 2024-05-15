import re

USER_CODE_BLOCK_REGEX = r"([ \t]*)\/\* User code start \[(.+)\]" \
                        r"[ \n]([\S\s]*)\*\/" \
                        r"([\S\s]*)\n" \
                        r"\1\/\* User code end \[\2\] \*\/"

indent = "    "


def init(new_indent: str):
    global indent
    indent = new_indent


def make_c_compatible(name: str, upper=False):
    if upper:
        name = name.upper()
    else:
        name = name.lower()
    return re.sub(r'\W+|^(?=\d)', '_', name).removesuffix("_")


def gen_enum(enums, values, name, depth=0, transform_enum_names=False):
    if transform_enum_names:
        transformed_enums = []
        for enum in enums:
            raw_enum = f"{name} {enum}"
            transformed_enums.append(make_c_compatible(raw_enum, upper=True))
    else:
        transformed_enums = enums.copy()
    lines = [f"{indent * depth}typedef enum {{"]
    max_len = len(max(transformed_enums, key=len))
    for enum, val in zip(transformed_enums, values):
        if val is not None:
            lines.append(f"{indent * (depth + 1)}{enum.ljust(max_len)} = {val},")
        else:
            lines.append(f"{indent * (depth + 1)}{enum},")
    lines.append(f"{indent * depth}}} {make_c_compatible(f'{name}_t')};")
    return lines


# Return a list of lines so that changing indent later is easier
def gen_c_array(elements, depth=0):
    lines = [f"{indent * depth}{{"]
    for elem in elements:
        if isinstance(elem, list):
            for el in elem:
                lines.append(f"{indent * (depth + 1)}{el}")
            lines[-1] += ","
        else:
            lines.append(f"{indent * (depth + 1)}{elem},")
    lines[-1] = lines[-1][:-1]
    lines.append(f"{indent * depth}}}")
    return lines


def gen_c_struct(elements, depth=0):
    lines = [f"{indent * depth}{{"]
    for elem in elements:
        field = elem["field"]
        val = elem["value"]
        if isinstance(val, list):
            lines.append(f"{indent * (depth + 1)}.{field} = ")
            for v in val:
                lines.append(f"{indent * (depth + 1)}{v}")
            lines[-1] += ","
        elif isinstance(val, bool):
            if val:
                lines.append(f"{indent * (depth + 1)}.{field} = true,")
            else:
                lines.append(f"{indent * (depth + 1)}.{field} = false,")
        else:
            lines.append(f"{indent * (depth + 1)}.{field} = {val},")
    lines[-1] = lines[-1][:-1]
    lines.append(f"{indent * depth}}}")
    return lines


def gen_protobuf_struct(elements, depth=0):
    raw_elements = []
    for elem in elements:
        if "oneOf" in elem:
            if "which" in elem:
                raw_elements.append({"field": f"which_{elem['oneOf']}", "value": f"{elem['which']}"})
            else:
                raw_elements.append({"field": f"which_{elem['oneOf']}", "value": f"{elem['field']}"})
            for el in elem['value']:
                if "optional" in el and el["optional"]:
                    raw_elements.append({"field": f"{elem['oneOf']}.{elem['field']}.has_{el['field']}", "value": True})
                raw_elements.append({"field": f"{elem['oneOf']}.{elem['field']}.{el['field']}", "value": el['value']})
        elif "optional" in elem and elem["optional"]:
            raw_elements.append({"field": f"has_{elem['field']}", "value": True})
            raw_elements.append({"field": elem['field'], "value": elem['value']})
        else:
            raw_elements.append({"field": elem['field'], "value": elem['value']})
    return gen_c_struct(raw_elements, depth=depth)


def get_user_code(contents: str) -> dict:
    matches = re.findall(USER_CODE_BLOCK_REGEX, contents)
    user_code = {}
    for code in matches:
        # The regex captures some other groups which we don't care about here
        n = code[1]  # Block name
        c = code[3]  # Code within block
        if n in user_code.keys() or "User code start [" in code[1]:
            raise ValueError(f"Found reused user code block name \"{n}\"")
        user_code[n] = c
    return user_code


def update_file_with_user_code(template: str, code_blocks: dict) -> str:
    matches = re.findall(USER_CODE_BLOCK_REGEX, template)
    new_keys = []
    for code in matches:
        new_keys.append(code[1])
    # Check that all of the code blocks in the old code are still present in the new code
    # Otherwise the user will lose the code in this section
    for key in code_blocks.keys():
        # Allowing the removal of code blocks as long as they were unused in the old code
        if key not in new_keys and code_blocks[key] != '':
            raise ValueError(f"Found user code block \"{key}\" which is being used in the old code but "
                             f"no longer exists in the new code")

    output = template
    # Put the old code back into the template
    for elem in re.finditer(USER_CODE_BLOCK_REGEX, template):
        groups = elem.groups()
        if groups[1] in code_blocks:
            existing = elem.group(0)
            if groups[2] != '':
                # Code block with an additional description
                replacement = f"{groups[0]}/* User code start [{groups[1]}]\n" \
                              f"{groups[2]}*/" \
                              f"{code_blocks[groups[1]]}\n" \
                              f"{groups[0]}/* User code end [{groups[1]}] */"
            else:
                # Basic code block with no description
                replacement = f"{groups[0]}/* User code start [{groups[1]}] */" \
                              f"{code_blocks[groups[1]]}\n" \
                              f"{groups[0]}/* User code end [{groups[1]}] */"
            output = output.replace(existing, replacement)
    return output

import re

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

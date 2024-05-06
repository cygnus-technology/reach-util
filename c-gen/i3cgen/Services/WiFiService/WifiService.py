import json
from i3cgen.utils import util

class Cli:
    def to_enum(param: json):
        return util.make_c_compatible(f"WIFI_{param['name']}", upper=True)

    def to_protobuf(param: json, depth=0):
        fields = []
        print(f"{__name__} not populated")
        return fields

def gen_definitions(service: json):
    lines = []
    lines.append("#define INCLUDE_WIFI_SERVICE")
    lines.append(f"#define NUM_WIFI_AP {service['AP count']}")
    return lines

def gen_enums(service: json):
    output = []
    print(f"{__name__} not populated")
    return output

def gen_variables(service: json):
    output = []
    print(f"{__name__} not populated")
    return output
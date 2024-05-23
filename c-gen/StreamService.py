import json
import CCodeUtils as ccu
import UserCodeUtils as ucu


class StreamService:
    class Stream:
        def __init__(self, stream: json):
            self.id = stream.get('id', None)
            self.name = stream['name']
            self.description = stream['description']
            self.access = stream['access']

        def as_enum(self) -> str:
            return ccu.make_c_compatible(f"STREAM_{self.name}", upper=True)

        def as_struct(self) -> ccu.CStruct:
            fields = [{'field': 'stream_id', 'value': self.as_enum()},
                      {'field': 'name', 'value': ccu.CString(self.name)},
                      {'field': 'description', 'value': ccu.CString(self.description)},
                      {'field': 'access', 'value': ccu.get_access_enum(self.access)}]
            return ccu.CStruct(fields, is_protobuf=True)

    def __init__(self, service: json):
        self.streams = [StreamService.Stream(f) for f in service['streams']]

    def get_file(self) -> ccu.CFile:
        output = ccu.CFile("streams",
                           "A minimal implementation of stream discovery and access",
                           ucu.get_template("streams.c"))
        enums = [ccu.CEnum([x.as_enum() for x in self.streams], [x.id for x in self.streams], "stream")]
        descriptions = [cmd.as_struct() for cmd in self.streams]
        output.contents[".h Defines"].append(ccu.CSnippet(f"#define NUM_STREAMS {len(self.streams)}"))
        output.contents[".h Data Types"] += enums
        output.contents[".c Local/Extern Variables"].append(
            ccu.CArray(descriptions, name="static cr_StreamInfo stream_descriptions"))
        return output

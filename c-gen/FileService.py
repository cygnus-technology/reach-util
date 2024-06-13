import json
import CCodeUtils as ccu
import UserCodeUtils as ucu


class FileService:
    class File:
        def __init__(self, file: json):
            self.id = file.get('id', None)
            self.name = file['name']
            self.access = file['access']
            self.storage_location = file['storageLocation']
            self.require_checksum = file['requireChecksum']
            self.max_size = file.get('maxSize', None)

        def as_enum(self) -> str:
            return ccu.make_c_compatible(f"FILE_{self.name}", upper=True)

        def as_struct(self) -> ccu.CStruct:
            fields = [{'field': 'file_id', 'value': self.as_enum()},
                      {'field': 'file_name', 'value': ccu.CString(self.name)},
                      {'field': 'access', 'value': ccu.get_access_enum(self.access)},
                      {'field': 'storage_location', 'value': ccu.get_storage_location_enum(self.storage_location)},
                      {'field': 'require_checksum', 'value': ccu.CBool(self.require_checksum)}]
            if self.max_size:
                fields.append({'field': 'maximum_size_bytes', 'value': self.max_size, 'optional': True})
            return ccu.CStruct(fields, is_protobuf=True)

    def __init__(self, service: json):
        self.files = [FileService.File(f) for f in service['files']]

    def get_file(self) -> ccu.CFile:
        output = ccu.CFile("files",
                           "A minimal implementation of file discovery and read/write handling",
                           ucu.get_template("files.c"))
        enums = [ccu.CEnum([x.as_enum() for x in self.files], [x.id for x in self.files], "file")]
        descriptions = [cmd.as_struct() for cmd in self.files]
        output.contents[".h Defines"].append(ccu.CSnippet(f"#define NUM_FILES {len(self.files)}"))
        output.contents[".h Data Types"] += enums
        output.contents[".c Local/Extern Variables"].append(
            ccu.CArray(descriptions, name="cr_FileInfo sFileDescriptions"))
        return output

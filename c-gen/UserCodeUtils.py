import re
from pathlib import Path
import shutil

USER_CODE_BLOCK_REGEX = r"([ \t]*)\/\* User code start \[(.+)\]" \
                        r"[ \n]([\S\s]*)\*\/" \
                        r"([\S\s]*)\n" \
                        r"\1\/\* User code end \[\2\] \*\/"

SUPPORTED_GENERATED_FILES = [
    "cli",
    "commands",
    "device",
    "files",
    "parameters",
    "streams",
    "time",
    "wifi"
]


user_templates = None


def config(user_template_location: Path):
    global user_templates
    user_templates = user_template_location


def backup_existing_files(src_path: Path, inc_path: Path):
    def back_up(path: Path):
        backup_path = Path(str(path) + ".bak")
        if path.exists():
            print(f"Backing up {path.name} as {backup_path.name}")
            shutil.copy2(path, backup_path)

    for svc in SUPPORTED_GENERATED_FILES:
        back_up(src_path.joinpath(f"{svc}.c"))
        back_up(inc_path.joinpath(f"{svc}.h"))


def get_user_code(contents: str) -> dict:
    matches = re.findall(USER_CODE_BLOCK_REGEX, contents)
    user_code = {}
    for code in matches:
        # The regex captures some other groups which we don't care about here
        n = code[1]  # Block name
        c = code[3]  # Code within block
        if n in user_code.keys() or "User code start [" in code[1]:
            raise ValueError(f"Found reused user code block name \"{n}\"")
        # Only add to the dictionary if the code block has something in it
        if c:
            user_code[n] = c
    return user_code


def get_all_user_code(src_path: Path, inc_path: Path):
    user_code = {}
    for svc in SUPPORTED_GENERATED_FILES:
        files = [src_path.joinpath(f"{svc}.c"), inc_path.joinpath(f"{svc}.h")]
        for f in files:
            if f.exists():
                new_user_code = get_user_code(open(f, "r").read())
                common_keys = set(user_code).intersection(set(new_user_code))
                if common_keys:
                    raise ValueError(f"Found the following duplicate user code blocks in {f.name}: {common_keys}")
                user_code |= new_user_code
    return user_code


def print_all_user_code(user_code: dict):
    for key in user_code.keys():
        print(f"/* User code start [{key}] */")
        print(user_code[key])
        print(f"/* User code end [{key}] */")


def get_template(path: str) -> str:
    template_path = Path(__file__).parent.joinpath("Templates", path).resolve()
    if user_templates:
        user_template_path = user_templates.joinpath(path).resolve()
        if user_template_path.is_file():
            template_path = user_template_path
    with open(template_path, "r") as f:
        output = f.read()
    return output


def get_template_code_blocks(template: str):
    matches = re.findall(USER_CODE_BLOCK_REGEX, template)
    keys = []
    for code in matches:
        keys.append(code[1])
    return keys


def update_file_with_user_code(template: str, code_blocks: dict) -> str:
    # matches = re.findall(USER_CODE_BLOCK_REGEX, template)
    # new_keys = []
    # for code in matches:
    #     new_keys.append(code[1])
    # # Check that all of the code blocks in the old code are still present in the new code
    # # Otherwise the user will lose the code in this section
    # for key in code_blocks.keys():
    #     # Allowing the removal of code blocks as long as they were unused in the old code
    #     if key not in new_keys and code_blocks[key] != '':
    #         raise ValueError(f"Found user code block \"{key}\" which is being used in the old code but "
    #                          f"no longer exists in the new code")

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


# print_all_user_code(get_all_user_code(Path("../reach-silabs/src"), Path("../reach-silabs/include")))
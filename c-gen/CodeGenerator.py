import sys
import argparse
import json
from pathlib import Path
import shutil
from termcolor import colored
import CCodeUtils as ccu
import UserCodeUtils as ucu
import Device
from Validator import DeviceDescriptionValidator


def main() -> int:
    """Main function for the generator"""
    parser = argparse.ArgumentParser(
        description='A script to transform a specification file defining a Reach device into C code')
    parser.add_argument('-d', '--definition', help="The .json file to parse", required=True, type=Path)
    parser.add_argument('-s', '--source-location', help="Where to put the generated *.c files",
                        required=True, type=Path)
    parser.add_argument('-i', '--include-location', help="Where to put the generated *.h files",
                        required=True, type=Path)
    parser.add_argument('-t', '--template-location', help="Where to draw user code templates from", type=Path)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--spaces', help="How many spaces to use for indent levels", type=int, default=4)
    group.add_argument('--tabs', help="How many tabs to use for indent levels", type=int)
    args = parser.parse_args()

    if args.tabs:
        ccu.config('\t' * args.tabs)
    else:
        ccu.config(' ' * args.spaces)

    # Validate the definition, source, and header paths
    if not Path(args.definition).exists():
        print(f'{args.definition} not found, exiting...')
        return -1
    print(f"Found definition file {args.definition.resolve()}")

    if not args.include_location.exists():
        print(f'{args.include_location} not found, exiting...')
        return -2
    print(f"Found include location, {args.include_location.resolve()}")

    if not args.source_location.exists():
        print(f'{args.source_location} not found, exiting...')
        return -3
    print(f"Found source location, {args.source_location.resolve()}")

    if args.template_location and not args.template_location.exists():
        print(f"Can't find reach-c-stack templates directory\n{args.template_location}\nexiting...")
        return -1

    # Create the schema validator, this can be reused
    # This assumes the schemas directory is relative to new-gen.py
    schema_dir = Path(__file__).parent.resolve()
    schema_dir = schema_dir.joinpath('schemas')
    validator = DeviceDescriptionValidator(str(schema_dir))

    # Load the file, this could potentially have JSON format errors
    with open(args.definition, "r") as f:
        print("Processing description file")
        device_description = json.load(f)

    # Do additional validation
    try:
        device_description = validator.validate(device_description)
        print(colored(f"Input file validated successfully.", 'green'))
    except Exception as e:
        print(colored(f"Input file validation FAILED.", 'red'))
        print(e)
        return -1

    new_device = Device.ReachDevice(device_description)
    generated_files = new_device.get_all_files()

    # Look for existing files and back these up
    ucu.backup_existing_files(args.source_location, args.include_location)

    # Reduce the files down to their user code blocks
    existing_user_code = ucu.get_all_user_code(args.source_location, args.include_location)

    # Make a list of the user code blocks present in the new files
    new_code_blocks = []
    for template in generated_files:
        new_code_blocks += ucu.get_template_code_blocks(template.gen_c_file())
        if template.h_file_needed():
            new_code_blocks += ucu.get_template_code_blocks(template.gen_h_file())

    # Verify that all old code blocks with code in them are still present
    for key in existing_user_code.keys():
        if key not in new_code_blocks:
            raise ValueError(f"Found user code block \"{key}\" which is being used in the old code but "
                             f"no longer exists in the new code")

    # Run `update_file_with_user_code()` command on every template file generated
    for file in generated_files:
        print(args.source_location.joinpath(f"{file.filename}.c"))
        updated_code = ucu.update_file_with_user_code(file.gen_c_file(), existing_user_code)
        with open(args.source_location.joinpath(f"{file.filename}.c"), "w") as f:
            f.write(updated_code)
        if file.h_file_needed():
            updated_code = ucu.update_file_with_user_code(file.gen_h_file(), existing_user_code)
            with open(args.include_location.joinpath(f"{file.filename}.h"), "w") as f:
                f.write(updated_code)


if __name__ == '__main__':
    sys.exit(main())

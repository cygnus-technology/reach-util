import sys
import argparse
import json
from pathlib import Path
import shutil
from termcolor import colored

from i3cgen.utils import util
from i3cgen.Validator import DeviceDescriptionValidator
from i3cgen.Services.ParameterRepository import ParamRepoService
from i3cgen.Services.FileService import FileService
from i3cgen.Services.CommandService import CommandService
from i3cgen.Services.CliService import CliService
from i3cgen.Services.StreamService import StreamService
from i3cgen.Services.WiFiService import WifiService

# Use a raw string to get formatting to print correctly
# pylint: disable=line-too-long
HEADER_STRING = r'''/********************************************************************************************
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
 * @file      definitions.h/.c
 * @brief     A minimal implementation of Reach data access.  Auto-generated by a Python script.
 * @copyright 2023-2024 i3 Product Development. All Rights Reserved.
 *
 * Original Author: Chuck Peplinski
 * Script Author: Joseph Peplinski
 * Script Author: Andrew Carlson
 *
 ********************************************************************************************/

'''

def generate_output(modules: list, template_dir: Path, output_dir: Path):
    '''Generate output using existing backup content and templates'''
    verbose_print = False

    for module in modules:
        t_in = template_dir.joinpath(f"template_{module}").with_suffix('.c')
        f_out = output_dir.joinpath(f"{module}").with_suffix('.c')
        f_bak = str(f_out) + '.bak'
        print(f"Generating {f_out}")

        if f_out.exists():
            print(colored(f"\tTemplate:\t{t_in}", 'yellow'))
            print(colored(f"\tBackup:\t\t{f_bak}", 'yellow'))

            with open(f_bak, 'r') as backup_file:
                backup_lines = backup_file.readlines()
            with open(t_in, 'r') as template_file:
                template_lines = template_file.readlines()

            line_num = 0
            processed = False
            # Open the output file for writing
            with open(f_out, 'w') as output_file:
                block_name = None
                user_code_started = False
                backup_index = 0
                for line in template_lines:
                    processed = False
                    line_num = line_num+1
                    #print("process line", line_num, "line", line, end="")
                    if user_code_started:
                        processed = True
                        if line.strip() == f"// User code end {block_name}":
                            user_code_started = False
                            if verbose_print:
                                print("user code end")
                        else:
                            if backup_index < len(backup_lines):
                                output_file.write(backup_lines[backup_index])
                                if verbose_print:
                                    print("wrote backup_lines[", backup_index, "]", backup_lines[backup_index], end="")
                            backup_index += 1
                            print("backup_index to", backup_index)
                    else:
                        if line.strip().startswith("// User code start"):
                            processed = True
                            block_name = line.split("[")[1].split("]")[0]
                            if verbose_print:
                                print("user code start, block_name ", block_name )
                                print("from template file, copy line", line_num, line, end="")
                            output_file.write(line)
                            user_code_started = True
                            # find backup_index for the start
                            backup_index = 0
                            while backup_index < len(backup_lines) and backup_lines[backup_index].strip() != f"// User code start [{block_name}]":
                                backup_index += 1
                            backup_index += 1  # step over the start
                            while backup_index < len(backup_lines) and backup_lines[backup_index].strip() != f"// User code end [{block_name}]":
                                output_file.write(backup_lines[backup_index])
                                if verbose_print:
                                    print("from user file, copy line [", backup_index, "]", backup_lines[backup_index], end="")
                                backup_index += 1

                            user_code_started = False
                            backup_index = 0
                    if processed is False:
                        if verbose_print:
                            print("from template file, copy line", line_num, line, end="")
                        output_file.write(line)
            print(colored("\tOutput updated from template.", 'green'))
        else:
            # Copy the template file to output directory
            shutil.copy(t_in, f_out)
            print(colored("\tInitial template file is copied", 'green'))
            print(colored(f"\t{f_out}", 'green'))

    return

def backup_definitions(src_path: Path, inc_path: Path):
    '''Backup the definitions.c/.h files'''
    original_src = src_path.joinpath('definitions').with_suffix('.c')
    original_inc = inc_path.joinpath('definitions').with_suffix('.h')
    backup = str(original_src) + '.bak'
    if original_src.exists():
        print(f"Backing up {original_src} as {backup}")
        shutil.copy2(original_src, backup)
    backup = str(original_inc) + '.bak'
    if original_inc.exists():
        print(f"Backing up {original_inc} as {backup}")
        shutil.copy2(original_inc, backup)

def generate_definitions(inc_path: Path, src_path: Path, defines: list, enums: list, values: list):
    print("Generating definitions.h\n")
    filename = inc_path.joinpath('definitions')
    with open(filename.with_suffix('.h'), "+w") as f:
        f.write(HEADER_STRING)
        f.write('#ifndef __DEFINITIONS_H__\n')
        f.write('#define __DEFINITIONS_H__\n')
        f.write('\n#include reach.pb.h\n\n')

        for group in defines:
            for line in group:
                f.write(f'{line}\n')
            f.write('\n')

        for group in enums:
            for enum in group:
                for line in enum:
                    f.write(f'{line}\n')
                f.write('\n')

        f.write('#endif /* __DEFINITIONS_H__ */\n')

    print("Generating definitions.c\n")
    filename = src_path.joinpath('defintions')
    with open(filename.with_suffix('.c'), '+w') as f:
        f.write(HEADER_STRING)
        f.write('#include \"definitions.h\"\n')
        f.write('\n')

        for group in values:
            for value in group:
                for line in value:
                    f.write(f'{line}\n')

        f.write('\n')

def discover_template_module_names(template_path: Path) -> list:
    '''Discover supported modules from the template directory'''
    modules = []
    for child in template_path.iterdir():
        filename = child.stem.removeprefix('template_')
        modules.append(filename)
    return modules

def backup_existing_src(src_path: Path, modules: list):
    '''Back up the existing module src files'''
    for mod in modules:
        filename = src_path.joinpath(f"{mod}").with_suffix('.c')
        backup_filename = str(filename) + '.bak'
        if filename.exists():
            print(f"Backing up {filename.name} as {backup_filename}")
            shutil.copy2(filename, backup_filename)
    print('')

def main() -> int:
    '''Main function for the generator'''
    parser = argparse.ArgumentParser(description='A script to transform a specification file defining a Reach device into C code')
    parser.add_argument('-d', '--definition', help="The .json file to parse", required=True)
    parser.add_argument('-s', '--source-location', help="Where to put the generated *.c files", required=True, type=Path)
    parser.add_argument('-i', '--include-location', help="Where to put the generated *.h files", required=True, type=Path)
    parser.add_argument('-t', '--template-location', help="Where to draw C code template files from",
                        default=Path(__file__).joinpath('..', '..', '..', 'reach-c-stack', 'templates').resolve(),
                        type=Path)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--spaces', help="How many spaces to use for indent levels", type=int, default=4)
    group.add_argument('--tabs', help="How many tabs to use for indent levels", type=int)

    args = parser.parse_args()

    if args.tabs:
        util.init('\t' * args.tabs)
    else:
        util.init(' ' * args.spaces)

    # Validate the definition, source, and header paths
    if not Path(args.definition).exists():
        print(f'{args.definition} not found, exiting...')
        return -1
    else:
        print(f"found definition file {args.definition}")

    if not args.include_location.exists():
        print(f'{args.include_location} not found, exiting...')
        return -2
    else:
        print(f"found include location, {args.include_location}")
    include_path = args.include_location

    if not args.source_location.exists():
        print(f'{args.source_location} not found, exiting...')
        return -3
    else:
        print(f"found source location, {args.source_location}")
    source_path = args.source_location

    if not args.template_location.exists():
        print(f"can't find reach-c-stack templates directory\n{args.template_location}\nexiting...")
        return -1
    else:
        print(f"found reach-c-stack templates, {args.template_location}")

    # Create the schema validator, this can be reused
    # This assumes the schemas directory is relative to new-gen.py
    schema_dir = Path(__file__).parent.resolve()
    schema_dir = schema_dir.joinpath('schemas')
    validator = DeviceDescriptionValidator(schema_dir)

    # Load the file, this could potentially have JSON format errors
    with open(args.definition, "r") as f:
        print("Processing description file")
        device_description = json.load(f)

    # Do additional validation
    try:
        device_description = validator.validate(device_description)
        print("Input file validated successfully.")
    except Exception as e:
        print(e)


    print("Generating defines, enums, values from enums...")
    define_groups = []
    enum_groups = []
    values_groups = []
    for service in device_description['services']:
        match service:
            case 'parameterRepositoryService':
                gen_defines = ParamRepoService.gen_definitions(device_description['services']['parameterRepositoryService'])
                define_groups.append(gen_defines)
                gen_enums = ParamRepoService.gen_enums(device_description['services']['parameterRepositoryService'])
                enum_groups.append(gen_enums)
                gen_values = ParamRepoService.gen_variables(device_description['services']['parameterRepositoryService'])
                values_groups.append(gen_values)
            case 'fileService':
                gen_defines = FileService.gen_definitions(device_description['services']['fileService'])
                define_groups.append(gen_defines)
                gen_enums = FileService.gen_enums(device_description['services']['fileService'])
                enum_groups.append(gen_enums)
                gen_values = FileService.gen_variables(device_description['services']['fileService'])
                values_groups.append(gen_values)
            case 'commandService':
                gen_defines = CommandService.gen_definitions(device_description['services']['commandService'])
                define_groups.append(gen_defines)
                gen_enums = CommandService.gen_enums(device_description['services']['commandService'])
                enum_groups.append(gen_enums)
                gen_values = CommandService.gen_variables(device_description['services']['commandService'])
                values_groups.append(gen_values)
            case 'cliService':
                gen_defines = CliService.gen_definitions(device_description['services']['cliService'])
                define_groups.append(gen_defines)
            case 'streamService':
                gen_defines = StreamService.gen_definitions(device_description['services']['streamService'])
                define_groups.append(gen_defines)
            case 'WiFService':
                gen_defines = WifiService.gen_definitions(device_description['services']['WiFService'])
                define_groups.append(gen_defines)
            case _:
                print(f"Service {service} is unspported")

    backup_definitions(source_path, include_path)
    generate_definitions(include_path, source_path, define_groups, enum_groups, values_groups)

    # Determine the module names from templates filenames
    module_names = discover_template_module_names(args.template_location)
    if len(module_names) == 0:
        print("No template files found")
        print ("exiting...")
        return -1
    else:
        print(f"found templates: {module_names}\n")

    # If we have existing source files
    # Back them up before proceeding
    backup_existing_src(source_path, module_names)

    # Generate our ouput files
    generate_output(module_names, args.template_location, source_path)

    return 0

if __name__ == '__main__':
    sys.exit(main())

import argparse
import json
import os
from pathlib import Path

from Python import util
from Python.Validator import DeviceDescriptionValidator
from Python.Services.ParameterRepository import ParamRepoService
from Python.Services.FileService import FileService
from Python.Services.CommandService import CommandService

parser = argparse.ArgumentParser(
                    description='A script to transform a specification file defining a Reach device into C code')
parser.add_argument('-d', '--definition', help="The .json file to parse", required=True)
parser.add_argument('-s', '--source-location', help="Where to put the generated 'definitions.c' file", default=".")
parser.add_argument('-i', '--include-location', help="Where to put the generated 'definitions.h' file", default=".")
group = parser.add_mutually_exclusive_group()
group.add_argument('--spaces', help="How many spaces to use for indent levels", type=int, default=4)
group.add_argument('--tabs', help="How many tabs to use for indent levels", type=int)

args = parser.parse_args()

if args.tabs:
    util.init('\t' * args.tabs)
else:
    util.init(' ' * args.spaces)

# Validate the definition, source, and header paths
def arg_to_path(arg_in):
    new_path = Path(arg_in)
    if not os.path.exists(new_path):
        new_path = None
    return new_path

definition_path = arg_to_path(args.definition)
if definition_path is None:
    print(f'-d file not found {args.definition}')
    print('qutting...')
    quit(-1)

include_path = arg_to_path(args.include_location)
if include_path is None:
    print(f'-i path not found {args.include_location}')
    print('quitting...')
    quit(-1)
else:
    print(f'saving include to {include_path}')

source_path = arg_to_path(args.source_location)
if source_path is None:
    print(f"-s path not found {args.source_location}")
    print('quitting...')
    quit(-1)
else:
    print(f'saving source to {source_path}')

# Create the schema validator, this can be reused
# This assumes the scheams directory is relative to new-gen.py
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


print("Generating Defines and Enums...")
define_groups = []
enum_groups = []
########################
# Parameter Repo Service
########################
if 'parameterRepositoryService' in device_description['services']:
    gen_defines = ParamRepoService.gen_definitions(device_description['services']['parameterRepositoryService'])
    define_groups.append(gen_defines)
    gen_enums = ParamRepoService.gen_enums(device_description['services']['parameterRepositoryService'])
    enum_groups.append(gen_enums)
    gen_values = ParamRepoService.gen_variables(device_description['services']['parameterRepositoryService'])

##############
# File Service
##############
if 'fileService' in device_description['services']:
    gen_defines = FileService.gen_definitions(device_description['services']['fileService'])
    define_groups.append(gen_defines)
    gen_enums = FileService.gen_enums(device_description['services']['fileService'])
    enum_groups.append(gen_enums)

##############
# Command Service
##############
if 'commandService' in device_description['services']:
    gen_defines = CommandService.gen_definitions(device_description['services']['commandService'])
    define_groups.append(gen_defines)
    gen_enums = CommandService.gen_enums(device_description['services']['commandService'])
    enum_groups.append(gen_enums)

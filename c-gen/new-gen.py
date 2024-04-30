import argparse
import json
import os

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

if args.source_location[-1] not in ["/", "\\"]:
    args.source_location += "/"
if args.include_location[-1] not in ["/", "\\"]:
    args.include_location += "/"

if args.tabs:
    util.init('\t' * args.tabs)
else:
    util.init(' ' * args.spaces)

# Create the schema validator, this can be reused
# This assumes the scheams directory is relative to new-gen.py
schema_dir = os.path.join(os.path.dirname(__file__), 'schemas')
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
########################
# Parameter Repo Service
########################
if 'parameterRepositoryService' in device_description['services']:
    test = ParamRepoService.gen_definitions(device_description['services']['parameterRepositoryService'])
    for line in test:
        print(line)
    print("")
    test = ParamRepoService.gen_enums(device_description['services']['parameterRepositoryService'])
    for enum in test:
        for line in enum:
            print(line)
        print("")

##############
# File Service
##############
if 'fileService' in device_description['services']:
    test = FileService.gen_definitions(device_description['services']['fileService'])
    for line in test:
        print(line)
    print("")
    test = FileService.gen_enums(device_description['services']['fileService'])
    for enum in test:
        for line in enum:
            print(line)
        print("")

##############
# Command Service
##############
if 'commandService' in device_description['services']:
    test = CommandService.gen_definitions(device_description['services']['commandService'])
    for line in test:
        print(line)
    print("")
    test = CommandService.gen_enums(device_description['services']['commandService'])
    for enum in test:
        for line in enum:
            print(line)
        print("")

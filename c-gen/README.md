# Reach C Code Generator Utility

## Overview
This is a utility for Reach device projects which are written in C, designed to simplify the process of implementing Reach services in a new project.  At a high level, this utility supports reading a JSON file which specifies the services (and elements within each service) for a Reach device, and generating a series of files implementing these services.  The scripts here provide one possible implementation of Reach services (particularly the parameter repository), which is not the most memory-efficient implementation possible, but is good enough for most projects.  This utility does not eliminate the need to write Reach-related firmware, but provides a reasonable framework for application-specific handling of Reach features.

# Requirements
[Python](https://www.python.org/downloads/) 3.10 or higher is required to run the scripts, though all development has been done in Python 3.11.  Additionally, the `jsonschema` and `referencing` packages are required.  Run `python -m pip install jsonschema referencing` to install these.

## Usage in Firmware Projects
Typically, a firmware project using this utility should include it as a submodule within git.  To generate the C files, run the `CodeGenerator.py` script with the relevant arguments (`python CodeGenerator.py -h` will show the available arguments).  Typically, these arguments will not change, so it may be convenient to have a script which calls `CodeGenerator.py` with the correct arguments.

For examples of projects using this utility, see the [nRF Connect Reach demo](https://github.com/cygnus-technology/reach-nrfc) or the [Silicon Labs Thunderboard Reach demo](https://github.com/cygnus-technology/reach-silabs).

## JSON File Formatting
The format of the JSON files used by this script is specified with a [JSON Schema](https://json-schema.org/).  The files for this specification may be found in the `schemas` folder, with `reachDevice.json` being the root specification file.  Eventually, a GUI editor will be available for creating device specification files, but for now these must be written by hand.  Before any code generation occurs, the script validates that the provided file matches the schema, and then does some additional validation which cannot easily be done with a JSON schema.  A large part of this validation is to make sure that parameter/file/command IDs and names are not repeated.

To specify that a device supports a service, the relevant service should be included in the `services` field.  The code generator currently does not support projects which use a hybrid of code-generator-based service implementations and custom service implementations, though it's possible to work around this if necessary.

## Code Generation
The code generator will create one .c/.h file pair per supported service (`parameters`, `files`, `commands`, `cli`, `streams`, and `wifi`).  `.h` files will only be created when necessary.  Additionally, `device.c/.h` will always be created.  The locations for the `.c` and `.h` files are specified separately with the `-i`/`--include-location` and `-s`/`--source-location` arguments, though these may point to the same folder.

`/* User code start [<description>] */` and `/* User code end [<description>] */` blocks are used to denote areas where user code can be put and will be preserved.  Regex is used to recognize these code blocks, so avoid creating comments of this same format within user code areas. Files which would be replaced by the code generator are backed up to `.bak` files before the new files are created.  User code blocks may be gained or lost due to changes to the JSON file.  If user code is present in a code block which will be lost, code will not be generated, and a warning will be printed about which user code blocks will be lost.

Most code styling is fixed, but the indentation style may be chosen with the `--spaces` or `--tabs` command line arguments.  By default, indentation is done with 4 spaces.

If desired, custom code templates may be provided in place of the default implementations.  To do this, the `-t` or `--template-location` argument should be provided with a path to a folder containing the same arrangement of files as are found in the `Templates` folder.  Only files with modified implementations need to be included in this folder, the default implementation will be used if a custom implementation is not found in the folder.  If the custom code requires changes to dynamically-generated elements, the Python scripts must be modified.  Code templates contain the information for both `.c` and `.h` files of the same name, and are not designed to be fully-valid C code.  If creating custom code templates, it is worth examining the code in `CCodeUtils.py` to see how templates are parsed into output code.  Note that template files use tabs for indentation, which are replaced with the selected indentation style before adding user code back into the files.

## Supported Services
Technically, a device may be created which supports no services, in which case only the `name`, `manufacturer`, and `description` of the device need to be provided (as well as an empty `services` array).  However, all devices are expected to support one or more services.  Parameters, extended labels, files, and commands all have optional `id` fields.  If these are not included, the `id` values will start from 0 and increment for each element in the array.  If an `id` field is included in one element, elements after this one will continue incrementing from this specified `id`.  This mechanism is also true of the `bitIndices` and `enumValues` arrays within extended labels.

### Parameter Repository
The parameter repository service is the most complex part of the specification file and code generator, as its elements are fairly tightly-defined.  Parameters have a number of fields which define their behavior, as well as some which only affect how they are displayed for the user.  Certain parameter types may have additional information associated with them, which are specified with extended labels.

#### Parameters
The specifications for parameters directly mirror the protobuf structures used to describe them.  The `labelName` field is optional, but if provided, it must match the name of an element within the `extendedLabels` array.

#### Extended Labels
Extended labels are used to describe the states of boolean, enumeration, and bitfield parameters more completely.  Internally, the discovery process will convert these into `cr_ParamExInfoResponse` structs, but custom structs are used by the code generator to store this information more efficiently.

### File Service
Like parameters, file specifications mirror the elements within the protobuf structures which describe them.  The `maxSize` element should be included if there is a hardware/firmware limitation for how large of a file can be stored.  The `Require Checksum` field determines whether to do additional validation during file transfers to ensure that the data is not corrupted.  The code generator does not handle any file storage, this is left to the user to implement.

### Command Service
Commands only consist of a name and a description.  It is up to the user to handle incoming commands in the `crcb_command_execute` function.

### Command Line Interface Service
The Reach protocol itself does not specify anything about the CLI service, other than that it can send and receive text data.  This code generator implements a rudimentary system for handling commands, including backspaces and providing a `help`/`?` command describing the available commands.  In addition to commands specified in the `commands` array, user code blocks are available for custom CLI handling.

### Time Service
The time service is very simple, only implementing a "get" and a "set" function.  This implementation is application-specific, so no information is contained within the time service specification.

### Stream Service
The definitions and generated code for streams are much like files, in that a majority of the implementation is left to the user to handle, but the code generator handles the discovery process.

### Wi-Fi Service
The Wi-Fi service also requires a very application-specific implementation.  Currently, it only handles generating an array of access point descriptions for the user to modify and report as needed.

## Planned Features

### Access Control
The Reach protocol supports providing a "challenge key" when connecting, which can be used to modify what is visible through Reach.  Eventually, the code generator intends to support customizable access levels, with the ability to exclude/include services or elements/features within services depending on the challenge key. 

### Protobuf Customization
In order to avoid dynamic memory allocation and limit memory usage, `reach-c-stack` (which this code generator works with) uses the [nanopb](https://github.com/nanopb/nanopb) library, which requires fixed limits on things such as string and bytearray lengths.  `reach-c-stack` currently uses size limits which are more of a "one size fits all" solution, but when provided a device specification file, these size limits can be optimized on a per-device basis.  However, this will require more development time, and introduces dependencies outside of Python and its libraries.

## Known Bugs and Limitations
This utility is very much a work-in-progress, as new Reach implementations expose oversights in its design and updates to the Reach protocol and C SDK require changes to the scripts.
 - Parameter, file, and command names are all used to generate associated enumerations within the C code, which requires that they are transformed into valid C names.  The script includes some handling for invalid characters, but there are many ways to create invalid enumerations through these names.
 - The script has no way of telling if the code it generated is valid C code.
 - The generated code formatting has some spacing issues, but these issues are only cosmetic.

## Contributing
To contribute, create an issue in the repository, and the team at i3 Product Development will respond as quickly as possible.

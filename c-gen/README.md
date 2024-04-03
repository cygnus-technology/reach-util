# Reach C Code Generator Utility

## Overview
This is a utility for Reach device projects which are written in C, designed to simplify the process of implementing Reach services in a new project.  At a high level, this utility supports reading an .xlsx file with a standard format (designed to be human-readable for app and firmware developers) and turning this into `definitions.c` and `definitions.h` C files.  The scripts here provide one possible implementation of Reach services (particularly the parameter repository), which is not the most memory-efficient implementation possible, but is good enough for most projects.  This utility does not eliminate the need to write Reach-related firmware, but provides a reasonable framework for application-specific handling of Reach features.

# Requirements
[Python](https://www.python.org/downloads/) 3.10 or higher is required to run the scripts, though all development has been done in Python 3.11.  Additionally, the `openpyxl` package is necessary for parsing .xlsx files.  Run `python -m pip install openpyxl` to install this.

## Usage in Firmware Projects
Typically, a firmware project using this utility should include it as a submodule within git.  To generate the C files, run the `c_code_generator.py` script with the relevant arguments (`python c_code_generator.py -h` will show the available arguments).  Typically, these arguments will not change, so it may be convenient to have a script which calls `c_code_generator.py` with the correct arguments.

Whenever the .xlsx file is changed, the script should be rerun.  `definitions.h` and `definitions.c` will be rewritten without regard to changes outside of the Python scripts, so these files should not be modified if the intention is to continue using the scripts.

For an example of a project using this utility, see the [nRF Connect Reach demo](https://github.com/cygnus-technology/reach-nrfc).

## .xlsx File Formatting
`Template.xlsx` is provided as a starting point for any new projects using the utility.  Where possible, cell validation is used to enforce limitations of the protocol, such as length limits for names and descriptions.  Cells with bold text should not be modified or removed, as they are required by the scripts.

### Device Information
The `Device Information` sheet is the only sheet required to be part of the file, and it defines the device information which will be sent from the device to the app and/or web portal.  All fields other than yes/no options are technically optional, though omitting the device name is not recommended.

The `Device Name`, `Manufacturer`, and `Device Description` fields should be fairly self-explanatory.  The `CLI Supported` and `Time Supported` enable the CLI and Time services, respectively.  These two services have no further information defined by the .xlsx file.  The `Application Identifier` and `Endpoints` fields are currently unused.  The `Application Identifier` is a UUID which is planned to allow the app and/or web portal to recognize certain devices and show a more customized UI for them.  The `Endpoints` field is a feature intended to allow multiple interconnected devices to communicate with Reach through a single BLE connection.

### Included Services
For Reach services other than the CLI and Time services, the inclusion of the relevant sheets is used to denote that the device will support these services.

### Parameters
The parameter repository service is the most complex part of this definition file.  Parameters have a number of fields which define their behavior, as well as some which only affect how they are displayed for the user.

 - Name: Self-explanatory
 - Type: The data type for the parameter.  Bitfields and enums are stored as unsigned 32-bit integers internally.  Strings and bytearrays may be up to 32 bytes.
 - Extended Type: This is only relevant for bitfields and enums.  By default, the script will look for an enum/bitfield description with the same name as the parameter name, but to associate multiple parameters with a single enum/bitfield description, the Extended Type should match the name of the desired description.
 - Description: Self-explanatory
 - Units: Shown after numerical parameters in the UI.
 - Size: Only used for bytearrays, the (default) size of the bytearray (in bytes).
 - Access: Self-explanatory.  An access type of `None` is technically supported, but this serves no practical purpose.
 - Minimum/Maximum Value: This defines the bounds of numerical parameters (ints, uints, and floats).
 - Default Value: This defines how the parameter will be initialized.  For numerical parameters, this value is straightforward.  The default value may also be used for bools (1 = `true`, 0 = `false`), and enums/bitfields (manually calculate the value associated with the desired default state)
 - Storage Location: The `RAM` and `NVM` options should be self-explanatory, while the meaning of the extended versions of these is up to the device.  Storage methods are implementation-specific, so it is up to the application to handle storing `NVM` parameters in a non-volatile manner.

Each non-empty row in the sheet beyond the labels in bold represents a parameter.  There is no limit to how many parameters may be defined, but parameter names may not repeat, and names should generally stick to ASCII characters.  The `Description`, `Units`, `Size`, `Minimum Value`, `Default Value`, and `Maximum Value` fields are optional.

The Reach Parameter Repository service supports non-consecutive parameter IDs as well as names, but currently this utility generates parameters with IDs increasing continuously from 0.

#### Enumerations and Bitfields
Bitfield and enumeration parameters may optionally have human-readable translations of some or all of their possible values.  These translations are defined in separate sheets named for their corresponding parameter (or Extended Type if this is provided).  `Template.xlsx` provides examples for the format of these sheets for enumerations and bitfields, which are slightly different.

Enumerations are made up of pairs of names and values, though the values are optional.  Each row represents a new name/value pair.  If the `Value` field is left blank for a row with a name, its value will be one greater than the value of the row before it (or 0 if it is the first value).  This allows for non-contiguous blocks of enumeration values.  Practically speaking, the only limit for the number of values in an enumeration is the amount of memory available on the processor.

Bitfield definitions work similarly, though they define a bit position rather than a value, with valid values being between 0 and 31.

### Files
Files are defined similarly to parameters, though with far fewer fields for each file.  All fields are required, and there is no limit on the maximum file size, but the file size must be greater than 0.  The file size is defined in bytes, and may be modified by the application as needed.  The `Require Checksum` field determines whether to do additional validation during file transfers to ensure that the data is not corrupted.

### Commands
Commands are defined very simply, with only a name and an optional description (which is not actually used in the C code).

## Known Bugs and Limitations
This utility is very much a work-in-progress, as new Reach implementations expose oversights in its design and updates to the Reach protocol and C SDK require changes to the scripts.
 - Parameter, file, and command names are all used to generate associated enumerations within the C code, which requires that they are transformed into valid C names.  The script includes some handling for invalid characters, but there are many ways to create invalid enumerations through these names.
 - The script has no way of telling if the code it generated is valid C code.

## Contributing
To contribute, create an issue in the repository, and the team at i3 Product Development will respond as quickly as possible.

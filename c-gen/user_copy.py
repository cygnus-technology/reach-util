import os
import shutil
from termcolor import colored

def copy_template_to_output(file_name, template_dir, output_dir):
    # Input and output file paths
    template_file_path = template_dir + file_name
    output_file_path = os.path.join(output_dir, file_name)

    verbose_print = False
    print("Generating", output_file_path, "from", template_file_path);
    # Check if the output file already exists
    if os.path.exists(output_file_path):
        # Rename the existing output file
        backup_file_path = os.path.join(output_dir, file_name + ".bak")
        shutil.move(output_file_path, backup_file_path)

        # Open the backup file for reading
        with open(backup_file_path, 'r') as backup_file:
            backup_lines = backup_file.readlines()

        # Open the template file for reading
        with open(template_file_path, 'r') as template_file:
            template_lines = template_file.readlines()

        line_num = 0
        processed = False
        # Open the output file for writing
        with open(output_file_path, 'w') as output_file:
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
                if processed == False:
                    if verbose_print:
                        print("from template file, copy line", line_num, line, end="")
                    output_file.write(line)
        print("Output file", file_name)
        print(colored(f"Output updated from template.", 'green'))
    else:
        # Copy the template file to output directory
        shutil.copy(template_file_path, output_file_path)
        print(colored(f"Initial template file is copied.", 'green'))

# To Do:  
# Call from a larger program.
# Take the directories from command line.
template_dir = "../../reach-c-stack/templates/template_"
output_dir = "../../src"
    
file_name = "device.c"
copy_template_to_output(file_name, template_dir, output_dir)

file_name = "streams.c"
copy_template_to_output(file_name, template_dir, output_dir)

file_name = "wifi.c"
copy_template_to_output(file_name, template_dir, output_dir)

file_name = "parameters.c"
copy_template_to_output(file_name, template_dir, output_dir)

file_name = "files.c"
copy_template_to_output(file_name, template_dir, output_dir)

file_name = "commands.c"
copy_template_to_output(file_name, template_dir, output_dir)

file_name = "time.c"
copy_template_to_output(file_name, template_dir, output_dir)



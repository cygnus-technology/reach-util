import json
import CCodeUtils as ccu
import UserCodeUtils as ucu


class CliService:
    class Command:
        def __init__(self, cmd: json):
            self.string = cmd['string']
            self.description = cmd.get('description', None)

    def __init__(self, service: json):
        self.commands = [CliService.Command(cmd) for cmd in service['commands']]

    def get_file(self) -> ccu.CFile:
        def generate_cli_handler() -> ccu.CFunction:
            # Mostly standard code, but with custom elements in the 'help' command handler,
            # and for all other command handlers
            start = '''\tif (*ins == '\\r' || *ins == '\\n')\n\t{\n\t\treturn 0;\n\t}\n\n''' \
                    '''\tif ((*ins == '?') || (!strncmp("help", ins, 4)))\n\t\t{\n'''
            middle = '\n\t\treturn 0;\n\t}\n\n\tcrcb_set_command_line(ins);\n' \
                     '\t// step through remote_command_table and execute if matching\n'''
            end = '''\n\t/* User code start [CLI: Custom command handling] */\n''' \
                  '''\t/* User code end [CLI: Custom command handling] */\n\telse\n''' \
                  '''\t\ti3_log(LOG_MASK_WARN, "CLI command '%s' not recognized.", ins, *ins);\n\treturn 0;'''
            help_text_lines = [f'\t\ti3_log(LOG_MASK_ALWAYS, "  {cmd.string}: {cmd.description}");'
                               for cmd in self.commands if cmd.description]
            help_text_lines = "\n".join(help_text_lines)
            cmd_handler_lines = []
            first_instance = True
            for cmd in self.commands:
                temp = [f'\telse if (!strncmp({ccu.CString(cmd.string)}, ins, {len(cmd.string)}))',
                        '\t{',
                        f"\t\t/* User code start [CLI: '{cmd.string}' handler] */",
                        f"\t\t/* User code end [CLI: '{cmd.string}' handler] */",
                        '\t}']
                if first_instance:
                    temp[0] = f'\tif (!strncmp({ccu.CString(cmd.string)}, ins, {len(cmd.string)}))'
                    first_instance = False
                cmd_handler_lines += temp
            cmd_handler_lines = "\n".join(cmd_handler_lines)

            return ccu.CFunction(decl="int crcb_cli_enter(const char *ins)",
                                 body=f"{start}{help_text_lines}{middle}{cmd_handler_lines}{end}")

        output = ccu.CFile("cli",
                           "A minimal command-line interface implementation",
                           ucu.get_template("cli.c"))
        output.contents[".c Cygnus Reach Callback Functions"].append(generate_cli_handler())
        return output

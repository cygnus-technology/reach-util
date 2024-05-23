/* Template code start [.h Includes] */
/* Template code end [.h Includes] */

/* Template code start [.c Includes] */
#include "i3_log.h"
#include "cr_stack.h"
/* Template code end [.c Includes] */

/* Template code start [.h Defines] */
/* Template code end [.h Defines] */

/* Template code start [.c Defines] */
/* Template code end [.c Defines] */

/* Template code start [.h Data Types] */
/* Template code end [.h Data Types] */

/* Template code start [.c Data Types] */
/* Template code end [.c Data Types] */

/* Template code start [.h Global Variables] */
/* Template code end [.h Global Variables] */

/* Template code start [.c Local/Extern Variables] */
static char input[64];
static uint8_t input_length = 0;
/* Template code end [.c Local/Extern Variables] */

/* Template code start [.h Global Functions] */

void cli_init(void)
{
  /* User code start [CLI: Init] */
  /* User code end [CLI: Init] */
  cli_write_prompt();
}

void cli_poll(void)
{
  if (input_length == sizeof(input))
  {
    i3_log(LOG_MASK_WARN, "CLI input too long, clearing");
    memset(input, 0, sizeof(input));
    input_length = 0;
    cli_write_prompt();
  }
  if (cli_read_char(&input[input_length]))
  {
    switch (input[input_length])
    {
      case '\r':
        cli_write("\r\n");
        if (input_length == 0)
        {
          cli_write_prompt();
          break; // No data, no need to call anything
        }
        input[input_length] = 0; // Null-terminate the string
        crcb_cli_enter((const char*) input);
        input_length = 0;
        memset(input, 0, sizeof(input));
        cli_write_prompt();
        break;
      case '\n':
        break; // Ignore, only expect '\r' for command execution
      case '\b':
        // Received a backspace
        if (input_length > 0)
        {
          input[--input_length] = 0;
          cli_write("\b \b");
        }
        break;
      default:
        // Still waiting for an input
        cli_write_char(input[input_length]);
        if (input_length < sizeof(input))
          input_length++;
        break;
    }
  }
}

/* Template code end [.h Global Functions] */

/* Template code start [.c Cygnus Reach Callback Functions] */
/* Template code end [.c Cygnus Reach Callback Functions] */

/* Template code start [.c Local Functions] */

static void cli_write_prompt(void)
{
    /* User code start [CLI: Write Prompt]
     * This is called after a command is sent and processed, indicating that the CLI is ready for a new prompt.
     * A typical implementation of this is to send a single '>' character. */
    /* User code end [CLI: Write Prompt] */
}

static void cli_write(char *text)
{
    /* User code start [CLI: Write]
     * This is where other output sources should be handled (for example, writing to a UART port)
     * This is called for outputs which are not necessary via BLE, such as clearing lines or handling backspaces */
    /* User code end [CLI: Write] */
}

static void cli_write_char(char c)
{
    /* User code start [CLI: Write Char]
     * This is used to write single characters, which may be handled differently from longer strings. */
    /* User code end [CLI: Write Char] */
}

static bool cli_read_char(char *received)
{
    /* User code start [CLI: Read]
     * This is where other input sources (such as a UART) should be handled.
     * This should be non-blocking, and return true if a character was received, or false if not. */
    /* User code end [CLI: Read] */
}

/* Template code end [.c Local Functions] */
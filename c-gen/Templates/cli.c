/* Template code start [.h Includes] */
#include <stdbool.h>
/* Template code end [.h Includes] */

/* Template code start [.c Includes] */
#include "i3_log.h"
#include "cr_stack.h"
#include "crcb_weak.h"
/* Template code end [.c Includes] */

/* Template code start [.h Defines] */
/* Template code end [.h Defines] */

/* Template code start [.c Defines] */
#ifndef CLI_MAX_LINE_LENGTH
#error CLI_MAX_LINE_LENGTH should be defined in reach_server.h
#endif // CLI_MAX_LINE_LENGTH
/* Template code end [.c Defines] */

/* Template code start [.h Data Types] */
/* Template code end [.h Data Types] */

/* Template code start [.c Data Types] */
/* Template code end [.c Data Types] */

/* Template code start [.h Global Variables] */
/* Template code end [.h Global Variables] */

/* Template code start [.c Local/Extern Variables] */
static char sInput[CLI_MAX_LINE_LENGTH];
static uint8_t sInputLength = 0;
#if (NUM_CMD_MEMORIES > 0) // 0 if undefined
  static size_t sInputIndex = 0;
#endif
/* Template code end [.c Local/Extern Variables] */

/* Template code start [.h Global Functions] */

void cli_init(void)
{
	/* User code start [CLI: Init] */
	/* User code end [CLI: Init] */
}

#if (NUM_CMD_MEMORIES > 0)
/**
 * Clears line
 */
void clear_line()
{
	i3_log(LOG_MASK_BARE|LOG_MASK_ALWAYS, EMPTY_LINE);
}

/**
 * Goes to previous command in history.
 */
void process_up()
{
	// Go back in command history
	cmd_hist_back(sInput, &sInputIndex);
	sInputLength = sInputIndex;

	// Display new command
	clear_line();
	i3_log(LOG_MASK_BARE|LOG_MASK_ALWAYS, "%c", CARRIAGE_RETURN);
	i3_log(LOG_MASK_BARE|LOG_MASK_ALWAYS, "%c", PROMPT);
	i3_log(LOG_MASK_BARE|LOG_MASK_ALWAYS, sInput, sInputIndex);
}

/**
 * Goes to more recent command in history.
 */
void process_down()
{
	// Go back in command history
	cmd_hist_fwd(sInput, &sInputIndex);
	sInputLength = sInputIndex;

	// Display new command
	clear_line();
	i3_log(LOG_MASK_BARE|LOG_MASK_ALWAYS, "%c", CARRIAGE_RETURN);
	i3_log(LOG_MASK_BARE|LOG_MASK_ALWAYS, "%c", PROMPT);
	i3_log(LOG_MASK_BARE|LOG_MASK_ALWAYS, sInput, sInputIndex);
}

/**
 * Moves command line cursor to previous character in current command.
 */
void process_left()
{
	if (sInputIndex > 0)
	{
		// Move Cursor to the left
		sInputIndex--;
		i3_log(LOG_MASK_BARE|LOG_MASK_ALWAYS, CURSOR_LEFT, 4);
	}
}

/**
 * Moves command line cursor to previous character in current command.
 */
void process_right()
{
	if (sInputIndex < CLI_MAX_LINE_LENGTH)
	{
		// Move Cursor to the right
		sInputIndex++;
		i3_log(LOG_MASK_BARE|LOG_MASK_ALWAYS, CURSOR_RIGHT, 4);
	}
}

// State machine for command history
char_state_e char_state = IDLE;

#endif // NUM_CMD_MEMORIES

/**
 * Gets and processes data from the command line
 * @return True if CLI data was received during the poll (from sources other than BLE), or false otherwise.
 */
bool cli_poll(void)
{
	if (sInputLength == sizeof(sInput))
	{
		i3_log(LOG_MASK_WARN, "CLI input too long, clearing");
		memset(sInput, 0, sizeof(sInput));
		sInputLength = 0;
		cli_write_prompt();
	}
#if (defined(NUM_CMD_MEMORIES) && (NUM_CMD_MEMORIES > 0))
	char inChar;
	if (cli_read_char(&inChar))
	{
		switch (char_state) {
			// State machine handles special characters
			case IDLE:
				if (inChar == ESCAPE)
				{
					char_state = SPEC_CHAR;
					break;
				}
				switch (inChar)
				{
					case '\r':
						cli_write("\r\n");
						if (sInputLength == 0)
						{
							cli_write_prompt();
							break; // No data, no need to call anything
						}
						sInput[sInputLength] = 0; // Null-terminate the string
						cmd_hist_cmd_exec(sInput);
						crcb_cli_enter((const char*) sInput);
						sInputLength = 0;
						sInputIndex = 0;
						memset(sInput, 0, sizeof(sInput));
						cli_write_prompt();
						break;
					case '\n':
						break; // Ignore, only expect '\r' for command execution
					case '\b':
						// Received a backspace
						if (sInputLength > 0)
						{
							sInput[--sInputLength] = 0;
							sInputIndex--;
							cli_write("\b \b");
						}
						break;
					default:
						// Still waiting for an input
						sInput[sInputIndex] = inChar;
						cli_write_char(inChar);
						if (sInputIndex < sizeof(sInput))
							sInputIndex++;
						if (sInputIndex > sInputLength)
							sInputLength = sInputIndex;
						break;
				}
				break;

			case SPEC_CHAR:
				if (inChar == '[')
					char_state = ARROW_KEY;
				else
					char_state = IDLE;
				break;

			case ARROW_KEY:
				// Process arrow key
				if (inChar == 'A')
					process_up();
				else if (inChar == 'B')
					process_down();
				else if (inChar == 'C')
					process_right();
				else if (inChar == 'D')
					process_left();
				// fall through
			default:
			case MODIFY:
				char_state = IDLE;
				break;
		}
		// i3_log(LOG_MASK_ALWAYS, "     %d, %d", sInputLength, sInputIndex);
		return true;
	}

#else // command line history is NOT used
	if (cli_read_char(&sInput[sInputLength]))
	{
		switch (sInput[sInputLength])
		{
			case '\r':
				cli_write("\r\n");
				if (sInputLength == 0)
				{
					cli_write_prompt();
					break; // No data, no need to call anything
				}
				sInput[sInputLength] = 0; // Null-terminate the string
				crcb_cli_enter((const char*) sInput);
				sInputLength = 0;
				memset(sInput, 0, sizeof(sInput));
				cli_write_prompt();
				break;
			case '\n':
				break; // Ignore, only expect '\r' for command execution
			case '\b':
				// Received a backspace
				if (sInputLength > 0)
				{
					sInput[--sInputLength] = 0;
					cli_write("\b \b");
				}
				break;
			default:
				// Still waiting for an input
				cli_write_char(sInput[sInputLength]);
				if (sInputLength < sizeof(sInput))
					sInputLength++;
				break;
		}
		return true;
	}
#endif  // NUM_CMD_MEMORIES
	return false;
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
	(void)text;
	/* User code end [CLI: Write] */
}

static void cli_write_char(char c)
{
	/* User code start [CLI: Write Char]
	 * This is used to write single characters, which may be handled differently from longer strings. */
	(void)c;
	/* User code end [CLI: Write Char] */
}

static bool cli_read_char(char *received)
{
	/* User code start [CLI: Read]
	 * This is where other input sources (such as a UART) should be handled.
	 * This should be non-blocking, and return true if a character was received, or false if not. */
	(void)received;
	/* User code end [CLI: Read] */
	return false;   // Default implementation, no input available
}

/* Template code end [.c Local Functions] */

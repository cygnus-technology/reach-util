/* Template code start [.h Includes] */
/* Template code end [.h Includes] */

/* Template code start [.c Includes] */
#include <stdint.h>
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
static int sCommandIndex = 0;
/* Template code end [.c Local/Extern Variables] */

/* Template code start [.h Global Functions] */
/* Template code end [.h Global Functions] */

/* Template code start [.c Cygnus Reach Callback Functions] */
int crcb_get_command_count()
{
	int i;
	int numAvailable = 0;
	for (i=0; i<NUM_COMMANDS; i++)
	{
		if (crcb_access_granted(cr_ServiceIds_COMMANDS, command_desc[i].id))
			numAvailable++;
	}
	return numAvailable;
}

int crcb_command_discover_next(cr_CommandInfo *cmd_desc)
{
	if (sCommandIndex >= NUM_COMMANDS)
	{
		I3_LOG(LOG_MASK_REACH, "%s: Command index %d indicates discovery complete.", __FUNCTION__, sCommandIndex);
		return cr_ErrorCodes_NO_DATA;
	}

	while (!crcb_access_granted(cr_ServiceIds_COMMANDS, command_desc[sCommandIndex].id))
	{
		I3_LOG(LOG_MASK_FILES, "%s: sCommandIndex (%d) skip, access not granted", __FUNCTION__, sCommandIndex);
		sCommandIndex++;
		if (sCommandIndex >= NUM_COMMANDS)
		{
			I3_LOG(LOG_MASK_PARAMS, "%s: skipped to sCommandIndex (%d) >= NUM_COMMANDS (%d)", __FUNCTION__, sCommandIndex, NUM_COMMANDS);
			return cr_ErrorCodes_NO_DATA;
		}
	}
	*cmd_desc = command_desc[sCommandIndex++];
	return 0;
}

int crcb_command_discover_reset(const uint32_t cid)
{
	if (cid >= NUM_COMMANDS)
	{
		i3_log(LOG_MASK_ERROR, "%s: Command ID %d does not exist.", __FUNCTION__, cid);
		return cr_ErrorCodes_INVALID_ID;
	}

	for (sCommandIndex = 0; sCommandIndex < NUM_COMMANDS; sCommandIndex++)
	{
		if (command_desc[sCommandIndex].id == cid) {
			if (!crcb_access_granted(cr_ServiceIds_COMMANDS, command_desc[sCommandIndex].id))
			{
				sCommandIndex = 0;
				break;
			}
			I3_LOG(LOG_MASK_PARAMS, "discover command reset (%d) reset to %d", cid, sCommandIndex);
			return 0;
		}
	}
	sCommandIndex = crcb_get_command_count();
	I3_LOG(LOG_MASK_PARAMS, "discover command reset (%d) reset defaults to %d", cid, sCommandIndex);
	return cr_ErrorCodes_INVALID_ID;
}

int crcb_command_execute(const uint8_t cid)
{
	int rval = 0;
	switch (cid)
	{
		/* User code start [Commands: Command Handler] */
		/* User code end [Commands: Command Handler] */
		default:
			rval = cr_ErrorCodes_INVALID_ID;
			break;
	}
	/* User code start [Commands: Command Handler Post-Switch] */
	/* User code end [Commands: Command Handler Post-Switch] */
	return rval;
}
/* Template code end [.c Cygnus Reach Callback Functions] */

/* Template code start [.c Local Functions] */
/* Template code end [.c Local Functions] */
/* Template code start [.h Includes] */
/* Template code end [.h Includes] */

/* Template code start [.c Includes] */
#include <stddef.h>
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
/* Template code end [.c Local/Extern Variables] */

/* Template code start [.h Global Functions] */
/* Template code end [.h Global Functions] */

/* Template code start [.c Cygnus Reach Callback Functions] */
int crcb_parameter_notification_init(const cr_ParameterNotifyConfig **pNoteArray, size_t *pNum)
{
	*pNum = NUM_DEFAULT_PARAMETER_NOTIFICATIONS;
	*pNoteArray = sParameterDefaultNotifications;
	return 0;
}
/* Template code end [.c Cygnus Reach Callback Functions] */

/* Template code start [.c Local Functions] */
/* Template code end [.c Local Functions] */
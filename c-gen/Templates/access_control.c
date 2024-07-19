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
#define FIND_ACCESS(array, id, bitfield, num_bits) ((array[id / (8 / num_bits)] & (0b11 << (num_bits * (id % (8 / num_bits))))) >> (num_bits * (id % 4)))

#define GET_PID_ACCESS(level, id) FIND_ACCESS(level.pids, id, 0b11, 2)
#define GET_PEI_ID_ACCESS(level, pei_id) FIND_ACCESS(level.pei_ids, pei_id, 0b1, 1)
/* Template code end [.c Defines] */

/* Template code start [.h Data Types] */
/* Template code end [.h Data Types] */

/* Template code start [.c Data Types] */
typedef struct
{
    uint8_t pids[(NUM_PARAMS * 2) / 8];
    uint8_t pei_ids[NUM_EX_PARAMS / 8];
} access_level_t;
/* Template code end [.c Data Types] */

/* Template code start [.h Global Variables] */
/* Template code end [.h Global Variables] */

/* Template code start [.c Local/Extern Variables] */
/* Template code end [.c Local/Extern Variables] */

/* Template code start [.h Global Functions] */
/* Template code end [.h Global Functions] */

/* Template code start [.c Cygnus Reach Callback Functions] */
/* Template code end [.c Cygnus Reach Callback Functions] */

/* Template code start [.c Local Functions] */
/* Template code end [.c Local Functions] */
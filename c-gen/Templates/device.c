/* Template code start [.h Includes] */
/* Template code end [.h Includes] */

/* Template code start [.c Includes] */
#include "i3_log.h"
#include "app_version.h"
#include "cr_stack.h"
/* Template code end [.c Includes] */

/* Template code start [.h Defines] */
/* Template code end [.h Defines] */

/* Template code start [.c Defines] */
#define TOSTRING_LAYER_ONE(x) #x
#define TOSTRING(x) TOSTRING_LAYER_ONE(x)

#ifdef DEV_BUILD
#define APP_VERSION_TAIL "-dev"
#else
#define APP_VERSION_TAIL ""
#endif // DEV_BUILD
/* Template code end [.c Defines] */

/* Template code start [.h Data Types] */
/* Template code end [.h Data Types] */

/* Template code start [.c Data Types] */
/* Template code end [.c Data Types] */

/* Template code start [.h Global Variables] */
/* Template code end [.h Global Variables] */

/* Template code start [.c Local/Extern Variables] */
static const char sAppVersion[] = TOSTRING(APP_MAJOR_VERSION) "." TOSTRING(APP_MINOR_VERSION) "." TOSTRING(APP_PATCH_VERSION) APP_VERSION_TAIL;
/* Template code end [.c Local/Extern Variables] */

/* Template code start [.h Global Functions] */
const char *get_app_version()
{
    return sAppVersion;
}
/* Template code end [.h Global Functions] */

/* Template code start [.c Cygnus Reach Callback Functions] */
// The stack will call this function.
// The const copy of the basis in flash is copied to RAM so that the device
// can overwrite varying data like SN and hash.
int crcb_device_get_info(const cr_DeviceInfoRequest *request, cr_DeviceInfoResponse *pDi)
{
    (void) request;
    memcpy(pDi, &device_info, sizeof(cr_DeviceInfoResponse));
    I3_LOG(LOG_MASK_REACH, "%s: %s\n", __FUNCTION__, device_info.device_name);

    sprintf(pDi->firmware_version, "%s", sAppVersion);

    /* User code start [Device: Get Info]
     * Here, further modifications can be made to the contents of pDi if needed */
    /* User code end [Device: Get Info] */

    return 0;
}
/* Template code end [.c Cygnus Reach Callback Functions] */

/* Template code start [.c Local Functions] */
/* Template code end [.c Local Functions] */
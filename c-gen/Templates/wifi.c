/* Template code start [.h Includes] */
/* Template code end [.h Includes] */

/* Template code start [.c Includes] */
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
static int sWiFi_index = 0;
static int sWiFi_count = 0;
static cr_WiFiDescription wifi_desc[MAX_NUM_WIFI_ACCESS_POINTS];
/* Template code end [.c Local/Extern Variables] */

/* Template code start [.h Global Functions] */
/* Template code end [.h Global Functions] */

/* Template code start [.c Cygnus Reach Callback Functions] */
/**
* @brief   crcb_discover_wifi
* @details Retrieve the requested information about the WiFi
 *         system. The discovery process may take some time the
 *         implementation can choose to return
 *         cr_ErrorCodes_INCOMPLETE to indicate that the
 *         discover command needs to be issued again until it
 *         succeeds. Other errors are reported via the result
 *         field.
* @param   request (input) Unused.
* @param   response (output) The requested info
* @return  returns cr_ErrorCodes_NO_ERROR or
*          cr_ErrorCodes_INCOMPLETE.
*/
int crcb_discover_wifi(const cr_DiscoverWiFi *request,
                             cr_DiscoverWiFiResponse *response)
{
    (void)request;
    response->result = cr_ErrorCodes_NOT_IMPLEMENTED;
    int rval = cr_ErrorCodes_INCOMPLETE;

    /* User code start [WiFi: Discover]
     * If you have not just launched a scan, launch one.
     * If you don't yet have data, return cr_ErrorCodes_INCOMPLETE.
     * The wifi_desc variable should be filled with available access points,
     * and sWiFi_count should be updated appropriately */
    /* User code end [WiFi: Discover] */
    return rval;
}

/**
* @brief   crcb_get_wifi_count
* @return  The number of wifi access points available to the
*          the device.
*/
int crcb_get_wifi_count()
{
    /* User code start [WiFi: Get Count] */
    /* User code end [WiFi: Get Count] */

    return sWiFi_count;
}

/**
* @brief   crcb_wifi_discover_reset
* @details The overriding implementation must reset a pointer
*          into a table of the available wifi access points
*          such that the next call to
*          crcb_wifi_discover_next() will return the description
*          of this access point.
* @param   cid The ID to which the wifi table pointer
*              should be reset.  0 for the first AP.
* @return  cr_ErrorCodes_NO_ERROR on success or a non-zero error like
*          cr_ErrorCodes_INVALID_PARAMETER.
*/
int crcb_wifi_discover_reset(const uint32_t cid)
{
    if (cid >= sWiFi_count)
    {
        sWiFi_index = NUM_WIFI_AP;
        return cr_ErrorCodes_INVALID_ID;
    }
    sWiFi_index = cid;
    return 0;
}

/**
* @brief   crcb_wifi_discover_next
* @details Gets the wifi description for the next wifi.
*          The overriding implementation must post-increment its pointer into
*          the wifi table.
* @param   cmd_desc Pointer to stack provided memory into which the
*               wifi description is to be copied.
* @return  cr_ErrorCodes_NO_ERROR on success or cr_ErrorCodes_INVALID_PARAMETER
*          if the last wifi has already been returned.
*/
int crcb_wifi_discover_next(cr_ConnectionDescription *conn_desc)
{
    if (sWiFi_index >= NUM_WIFI_AP)
        return cr_ErrorCodes_INVALID_ID;

    if (sWiFi_index >= sWiFi_count)
        return cr_ErrorCodes_INVALID_PARAMETER;

    *conn_desc = wifi_desc[sWiFi_index];
    sWiFi_index++;
    return 0;
}

/**
* @brief   crcb_wifi_connection
* @details Establish or break a WiFi connection.
* @param   request (input) what needed to connect
* @param   response (output) result
* @return  returns zero or an error code
*/
int crcb_wifi_connection(const cr_WiFiConnectionRequest *request,
                               cr_WiFiConnectionResponse *response)
{
    affirm(request);
    affirm(response);

    /* User code start [WiFi: Connect/Disconnect] */
    /* User code end [WiFi: Connect/Disconnect] */

    return 0;
}
/* Template code end [.c Cygnus Reach Callback Functions] */

/* Template code start [.c Local Functions] */
/* Template code end [.c Local Functions] */
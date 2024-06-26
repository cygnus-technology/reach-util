/* Template code start [.h Includes] */
/* Template code end [.h Includes] */

/* Template code start [.c Includes] */
#include <stdint.h>
#include "cr_stack.h"
#include "i3_log.h"
#include "i3_error.h"
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
static int sSidIndex = 0;
/* Template code end [.c Local/Extern Variables] */

/* Template code start [.h Global Functions] */
/* Template code end [.h Global Functions] */

/* Template code start [.c Cygnus Reach Callback Functions] */
/**
* @brief   crcb_stream_get_count
* @return  The overriding implementation must returns the number
*          of streams implemented by the device.
*/
int crcb_stream_get_count()
{
    int i;
    int numAvailable = 0;
    for (i = 0; i < NUM_STREAMS; i++)
    {
        if (crcb_access_granted(cr_ServiceIds_STREAMS, sStreamDescriptions[i].stream_id)) numAvailable++;
    }
    return numAvailable;
}

/**
* @brief   crcb_stream_discover_reset
* @details The overriding implementation must reset a pointer into the stream
*          table such that the next call to crcb_stream_discover_next() will
*          return the description of this stream.
* @param   sid The ID to which the stream table pointer
*              should be reset.  use 0 for the first command.
* @return  cr_ErrorCodes_NO_ERROR on success or a non-zero error like
*          cr_ErrorCodes_INVALID_PARAMETER.
*/
int crcb_stream_discover_reset(const uint8_t sid)
{
    int rval = 0;
    uint8_t idx;
    rval = sFindIndexFromSid(sid, &idx);
    if (0 != rval)
    {
        I3_LOG(LOG_MASK_ERROR, "%s(%d): invalid SID, using NUM_STREAMS.", __FUNCTION__, sid);
        sSidIndex = NUM_STREAMS;
        return cr_ErrorCodes_INVALID_ID;
    }
    if (!crcb_access_granted(cr_ServiceIds_FILES, sStreamDescriptions[sSidIndex].stream_id))
    {
        I3_LOG(LOG_MASK_ERROR, "%s(%d): Access not granted, using NUM_STREAMS.", __FUNCTION__, sid);
        sSidIndex = NUM_STREAMS;
        return cr_ErrorCodes_INVALID_ID;
    }
    sSidIndex = idx;

    return 0;
}

/**
* @brief   crcb_stream_discover_next
* @details Gets the  description for the next stream.
*          The overriding implementation must post-increment its pointer into
*          the stream table.
* @param   stream_desc Pointer to stack provided memory into which the
*               stream description is to be copied.
* @return  cr_ErrorCodes_NO_ERROR on success or cr_ErrorCodes_INVALID_PARAMETER
*          if the last stream has already been returned.
*/
int crcb_stream_discover_next(cr_StreamInfo *stream_desc)
{
    if (sSidIndex >= NUM_STREAMS) // end of search
        return cr_ErrorCodes_NO_DATA;

    while (!crcb_access_granted(cr_ServiceIds_STREAMS, sStreamDescriptions[sSidIndex].stream_id))
    {
        I3_LOG(LOG_MASK_WARN, "%s: sSidIndex (%d) skip, access not granted",
               __FUNCTION__, sSidIndex);
        sSidIndex++;
        if (sSidIndex >= NUM_STREAMS)
        {
            I3_LOG(LOG_MASK_WARN, "%s: skipped to sSidIndex (%d) >= NUM_STREAMS (%d)",
                   __FUNCTION__, sSidIndex, NUM_STREAMS);
            return cr_ErrorCodes_NO_DATA;
        }
    }
    *stream_desc = sStreamDescriptions[sSidIndex++];
    return 0;
}

/**
* @brief   crcb_stream_get_description
* @details Get the description matching the stream ID.
* @param   sid The ID of the desired stream.
* @param   stream_desc Pointer to stack provided memory into which the
*               stream description is to be copied
* @return  cr_ErrorCodes_NO_ERROR on success or a non-zero error like
*          cr_ErrorCodes_INVALID_PARAMETER.
*/
int crcb_stream_get_description(uint32_t sid, cr_StreamInfo *stream_desc)
{
    int rval = 0;
    affirm(stream_desc != NULL);
    uint8_t idx;
    rval = sFindIndexFromSid(sid, &idx);
    if (rval != 0) return rval;
    *stream_desc = sStreamDescriptions[idx];
    /* User code start [Streams: Get Description] */
    /* User code end [Streams: Get Description] */
    return 0;
}

/**
* @brief   crcb_stream_read
* @details The stream flows from the device.
*           Prepare a StreamData packet to be sent to the
*           client.  This is called in the main Reach loop.
* @param   sid The ID of the desired stream.
* @param   data Pointer to stack provided memory into which the
*               data is to be copied
* @return  cr_ErrorCodes_NO_ERROR when the data is ready to be
*          sent.  cr_ErrorCodes_NO_DATA if there is no data to
*          be sent.
*/
int crcb_stream_read(uint32_t sid, cr_StreamData *data)
{
    int rval = cr_ErrorCodes_NO_DATA;
    affirm(data != NULL);
    uint8_t idx;
    rval = sFindIndexFromSid(sid, &idx);
    if (rval != 0) return cr_ErrorCodes_NO_DATA;

    /* User code start [Streams: Read] */
    /* User code end [Streams: Read] */
    return rval;
}

/**
* @brief   crcb_stream_write
* @details The stream flows to the device.
*           Record or consume this data provided by the client.
*           Increment and populate the roll count.
* @param   sid The ID of the desired stream.
* @param   data Pointer to stack provided memory containing the
*               stream data to be populated.
* @return  cr_ErrorCodes_NO_ERROR on success or a non-zero error like
*          cr_ErrorCodes_INVALID_PARAMETER.
*/
int crcb_stream_write(uint32_t sid, cr_StreamData *data)
{
    int rval = 0;
    affirm(data != NULL);
    uint8_t idx;
    rval = sFindIndexFromSid(sid, &idx);
    if (rval != 0) return rval;

    /* User code start [Streams: Write] */
    /* User code end [Streams: Write] */
    return rval;
}

/**
* @brief   crcb_stream_open
* @details Open the stream matching the stream ID. Zero the roll
*          count for this stream.
* @param   sid The ID of the desired stream.
* @return  cr_ErrorCodes_NO_ERROR on success or a non-zero error like
*          cr_ErrorCodes_INVALID_PARAMETER.
*/
int crcb_stream_open(uint32_t sid)
{
    int rval = 0;
    uint8_t idx;
    rval = sFindIndexFromSid(sid, &idx);
    if (rval != 0) return rval;

    /* User code start [Streams: Open] */
    /* User code end [Streams: Open] */
    return rval;
}

/**
* @brief   crcb_stream_close
* @details Close the stream matching the stream ID.
* @param   sid The ID of the desired stream.
* @return  cr_ErrorCodes_NO_ERROR on success or a non-zero error like
*          cr_ErrorCodes_INVALID_PARAMETER.
*/
int crcb_stream_close(uint32_t sid)
{
    int rval = 0;
    uint8_t idx;
    rval = sFindIndexFromSid(sid, &idx);
    if (rval != 0) return rval;

    /* User code start [Streams: Close] */
    /* User code end [Streams: Close] */
    return rval;
}
/* Template code end [.c Cygnus Reach Callback Functions] */

/* Template code start [.c Local Functions] */
static int sFindIndexFromSid(uint32_t sid, uint8_t *index)
{
    uint8_t idx;
    for (idx=0; idx<NUM_STREAMS; idx++) {
        if (sStreamDescriptions[idx].stream_id == sid) {
            *index = idx;
            return 0;
        }
    }
    return cr_ErrorCodes_INVALID_ID;
}
/* Template code end [.c Local Functions] */
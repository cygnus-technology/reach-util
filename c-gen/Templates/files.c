/* Template code start [.h Includes] */
#include "cr_stack.h"
/* Template code end [.h Includes] */

/* Template code start [.c Includes] */
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
static int sFidIndex = 0;
/* Template code end [.c Local/Extern Variables] */

/* Template code start [.h Global Functions] */
void files_init(void)
{
	/* User code start [Files: Init] */
	/* User code end [Files: Init] */
}

int files_set_description(uint32_t fid, cr_FileInfo *file_desc)
{
	int rval = 0;
	affirm(file_desc != NULL);
	uint32_t idx;
	rval = sFindIndexFromFid(fid, &idx);
	if (rval != 0)
		return rval;

	/* User code start [Files: Set Description]
	 * If the file description needs to be updated (for example, changing the current size), now's the time */
	/* User code end [Files: Set Description] */

	sFileDescriptions[idx] = *file_desc;

	return rval;
}
/* Template code end [.h Global Functions] */

/* Template code start [.c Cygnus Reach Callback Functions] */
int crcb_file_get_description(uint32_t fid, cr_FileInfo *file_desc)
{
	int rval = 0;
	affirm(file_desc != NULL);
	uint32_t idx;
	rval = sFindIndexFromFid(fid, &idx);
	if (rval != 0)
		return rval;

	/* User code start [Files: Get Description]
	 * If the file description needs to be updated (for example, changing the current size), now's the time */
	/* User code end [Files: Get Description] */

	*file_desc = sFileDescriptions[idx];

	return rval;
}

int crcb_file_get_file_count()
{
	int i;
	int numAvailable = 0;
	for (i = 0; i < NUM_FILES; i++)
	{
		if (crcb_access_granted(cr_ServiceIds_FILES, sFileDescriptions[i].file_id)) numAvailable++;
	}
	return numAvailable;
}

int crcb_file_discover_reset(const uint8_t fid)
{
	int rval = 0;
	uint32_t idx;
	rval = sFindIndexFromFid(fid, &idx);
	if (0 != rval)
	{
		I3_LOG(LOG_MASK_ERROR, "%s(%d): invalid FID, using NUM_FILES.", __FUNCTION__, fid);
		sFidIndex = NUM_FILES;
		return cr_ErrorCodes_INVALID_ID;
	}
	if (!crcb_access_granted(cr_ServiceIds_FILES, sFileDescriptions[sFidIndex].file_id))
	{
		I3_LOG(LOG_MASK_ERROR, "%s(%d): Access not granted, using NUM_FILES.", __FUNCTION__, fid);
		sFidIndex = NUM_FILES;
		return cr_ErrorCodes_BAD_FILE;
	}
	sFidIndex = idx;
	return 0;
}

int crcb_file_discover_next(cr_FileInfo *file_desc)
{
	if (sFidIndex >= NUM_FILES) // end of search
		return cr_ErrorCodes_NO_DATA;

	while (!crcb_access_granted(cr_ServiceIds_FILES, sFileDescriptions[sFidIndex].file_id))
	{
		I3_LOG(LOG_MASK_FILES, "%s: sFidIndex (%d) skip, access not granted",
			   __FUNCTION__, sFidIndex);
		sFidIndex++;
		if (sFidIndex >= NUM_FILES)
		{
			I3_LOG(LOG_MASK_PARAMS, "%s: skipped to sFidIndex (%d) >= NUM_FILES (%d)", __FUNCTION__, sFidIndex, NUM_FILES);
			return cr_ErrorCodes_NO_DATA;
		}
	}
	int rval = crcb_file_get_description(sFileDescriptions[sFidIndex].file_id, file_desc);
	sFidIndex++;
	return rval;
}
// which file
// offset, negative value specifies current location.
// how many bytes to read
// where the data goes
// bytes actually read, negative for errors.
int crcb_read_file(const uint32_t fid, const int offset, const size_t bytes_requested, uint8_t *pData, int *bytes_read)
{
	int rval = 0;
	uint32_t idx;
	rval = sFindIndexFromFid(fid, &idx);
	if (0 != rval)
	{
		I3_LOG(LOG_MASK_ERROR, "%s(%d): invalid FID.", __FUNCTION__, fid);
		return cr_ErrorCodes_INVALID_ID;
	}
	if (bytes_requested > REACH_BYTES_IN_A_FILE_PACKET)
	{
		I3_LOG(LOG_MASK_ERROR, "%s: %d is more than the buffer for a file read (%d).", __FUNCTION__, fid, REACH_BYTES_IN_A_FILE_PACKET);
		return cr_ErrorCodes_BUFFER_TOO_SMALL;
	}

	/* User code start [Files: Read]
	 * The code generator does nothing to handle storing files, so this is where pData and bytes_read should be updated */
	/* User code end [Files: Read] */

	return rval;
}

int crcb_file_prepare_to_write(const uint32_t fid, const size_t offset, const size_t bytes)
{
	int rval = 0;
	uint32_t idx;
	rval = sFindIndexFromFid(fid, &idx);
	if (0 != rval)
	{
		I3_LOG(LOG_MASK_ERROR, "%s(%d): invalid FID.", __FUNCTION__, fid);
		return cr_ErrorCodes_INVALID_ID;
	}
	/* User code start [Files: Pre-Write]
	 * This is the opportunity to prepare for a file write, or to reject it. */
	/* User code end [Files: Pre-Write] */
	return rval;
}

// which file
// offset, negative value specifies current location.
// how many bytes to write
// where to get the data from
int crcb_write_file(const uint32_t fid, const int offset, const size_t bytes, const uint8_t *pData)
{
	int rval = 0;
	uint32_t idx;
	rval = sFindIndexFromFid(fid, &idx);
	if (0 != rval)
	{
		I3_LOG(LOG_MASK_ERROR, "%s(%d): invalid FID.", __FUNCTION__, fid);
		return cr_ErrorCodes_INVALID_ID;
	}
	/* User code start [Files: Write]
	 * Here is where the received data should be copied to wherever the application is storing it */
	/* User code end [Files: Write] */
	return rval;
}

int crcb_file_transfer_complete(const uint32_t fid)
{
	int rval = 0;
	uint32_t idx;
	rval = sFindIndexFromFid(fid, &idx);
	if (0 != rval)
	{
		I3_LOG(LOG_MASK_ERROR, "%s(%d): invalid FID.", __FUNCTION__, fid);
		return cr_ErrorCodes_INVALID_ID;
	}
	/* User code start [Files: Write Complete]
	 * This allows the application to handle any actions which need to occur after a file has successfully been written */
	/* User code end [Files: Write Complete] */
	return rval;
}

// returns zero or an error code
int crcb_erase_file(const uint32_t fid)
{
	int rval = 0;
	uint32_t idx;
	rval = sFindIndexFromFid(fid, &idx);
	if (0 != rval)
	{
		I3_LOG(LOG_MASK_ERROR, "%s(%d): invalid FID.", __FUNCTION__, fid);
		return cr_ErrorCodes_INVALID_ID;
	}
	/* User code start [Files: Erase]
	 * The exact meaning of "erasing" is user-defined, depending on how files are stored by the application */
	/* User code end [Files: Erase] */
	return rval;
}
/* Template code end [.c Cygnus Reach Callback Functions] */

/* Template code start [.c Local Functions] */
static int sFindIndexFromFid(uint32_t fid, uint32_t *index)
{
	uint32_t idx;
	for (idx = 0; idx < NUM_FILES; idx++)
	{
		if (sFileDescriptions[idx].file_id == fid)
		{
			*index = idx;
			return 0;
		}
	}
	return cr_ErrorCodes_INVALID_ID;
}
/* Template code end [.c Local Functions] */
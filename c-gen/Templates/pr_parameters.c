/* Template code start [.h Includes] */
#include <stdbool.h>
#include <stdint.h>
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
static int sCurrentParameter = 0;
static cr_ParameterValue sParameterValues[NUM_PARAMS];
/* Template code end [.c Local/Extern Variables] */

/* Template code start [.h Global Functions] */
void parameters_init(void)
{
	/* User code start [Parameter Repository: Pre-Init]
	 * Here is the place to do any initialization required before individual parameters are initialized */
	/* User code end [Parameter Repository: Pre-Init] */
	memset(sParameterValues, 0, sizeof(sParameterValues));
	for (int i = 0; i < NUM_PARAMS; i++)
	{
		sParameterValues[i].parameter_id = sParameterDescriptions[i].id;
		// Convert from description type identifier to value type identifier
		sParameterValues[i].which_value = (sParameterDescriptions[i].which_desc - cr_ParameterInfo_uint32_desc_tag) + cr_ParameterValue_uint32_value_tag;

		parameters_reset_param(sParameterValues[i].parameter_id, false, 0);

		/* User code start [Parameter Repository: Parameter Init]
		 * Here is the place to do any initialization specific to a certain parameter */
		/* User code end [Parameter Repository: Parameter Init] */

	} // end for

	/* User code start [Parameter Repository: Post-Init]
	 * Here is the place to do any initialization required after parameters have been initialized */
	/* User code end [Parameter Repository: Post-Init] */
}

int parameters_reset_param(param_t pid, bool write, uint32_t write_timestamp)
{
	uint32_t idx;
	int rval = sFindIndexFromPid(pid, &idx);
	if (rval)
		return rval;
	
	cr_ParameterValue param = {
		.parameter_id = sParameterValues[idx].parameter_id,
		.which_value = sParameterValues[idx].which_value
	};
	
	switch (param.which_value - cr_ParameterValue_uint32_value_tag)
	{
		case cr_ParameterDataType_UINT32:
			if (sParameterDescriptions[idx].desc.uint32_desc.has_default_value)
				param.value.uint32_value = sParameterDescriptions[idx].desc.uint32_desc.default_value;
			break;
		case cr_ParameterDataType_INT32:
			if (sParameterDescriptions[idx].desc.int32_desc.has_default_value)
				param.value.int32_value = sParameterDescriptions[idx].desc.int32_desc.default_value;
			break;
		case cr_ParameterDataType_FLOAT32:
			if (sParameterDescriptions[idx].desc.float32_desc.has_default_value)
				param.value.float32_value = sParameterDescriptions[idx].desc.float32_desc.default_value;
			break;
		case cr_ParameterDataType_UINT64:
			if (sParameterDescriptions[idx].desc.uint64_desc.has_default_value)
				param.value.uint64_value = sParameterDescriptions[idx].desc.uint64_desc.default_value;
			break;
		case cr_ParameterDataType_INT64:
			if (sParameterDescriptions[idx].desc.int64_desc.has_default_value)
				param.value.int64_value = sParameterDescriptions[idx].desc.int64_desc.default_value;
			break;
		case cr_ParameterDataType_FLOAT64:
			if (sParameterDescriptions[idx].desc.float64_desc.has_default_value)
				param.value.float64_value = sParameterDescriptions[idx].desc.float64_desc.default_value;
			break;
		case cr_ParameterDataType_BOOL:
			if (sParameterDescriptions[idx].desc.bool_desc.has_default_value)
				param.value.bool_value = sParameterDescriptions[idx].desc.bool_desc.default_value;
			break;
		case cr_ParameterDataType_STRING:
			if (sParameterDescriptions[idx].desc.string_desc.has_default_value)
			{
				memcpy(param.value.string_value, sParameterDescriptions[idx].desc.string_desc.default_value, sizeof(sParameterDescriptions[idx].desc.string_desc.default_value));
			}
			break;
		case cr_ParameterDataType_ENUMERATION:
			if (sParameterDescriptions[idx].desc.enum_desc.has_default_value)
				param.value.enum_value = sParameterDescriptions[idx].desc.enum_desc.default_value;
			break;
		case cr_ParameterDataType_BIT_FIELD:
			if (sParameterDescriptions[idx].desc.bitfield_desc.has_default_value)
				param.value.bitfield_value = sParameterDescriptions[idx].desc.bitfield_desc.default_value;
			break;
		case cr_ParameterDataType_BYTE_ARRAY:
			if (sParameterDescriptions[idx].desc.bytearray_desc.has_default_value)
			{
				param.value.bytes_value.size = sParameterDescriptions[idx].desc.bytearray_desc.default_value.size;
				memcpy(param.value.bytes_value.bytes, sParameterDescriptions[idx].desc.bytearray_desc.default_value.bytes, sizeof(sParameterDescriptions[idx].desc.bytearray_desc.default_value.bytes));
			}
			else
			{
				param.value.bytes_value.size = sParameterDescriptions[idx].desc.bytearray_desc.max_size;
			}
			break;
		default:
			affirm(0);  // should not happen.
			break;
	}  // end switch
	
	/* User code start [Parameter Repository: Parameter Reset]
	 * Here is the place to add any application-specific behavior for handling parameter resets */
	/* User code end [Parameter Repository: Parameter Reset] */
	
	if (write)
	{
		param.timestamp = write_timestamp;
		rval = crcb_parameter_write(param.parameter_id, &param);
	}
	else
	{
		param.timestamp = sParameterValues[idx].timestamp;
		sParameterValues[idx] = param;
	}
	return rval;
}
/* Template code end [.h Global Functions] */

/* Template code start [.c Cygnus Reach Callback Functions] */
// Resets the application's pointer into the parameter table such that
// the next call to crcb_parameter_discover_next() will return the
// description of this parameter.
int crcb_parameter_discover_reset(const uint32_t pid)
{
	int rval = 0;
	uint32_t idx;
	rval = sFindIndexFromPid(pid, &idx);
	if (0 != rval)
	{
		sCurrentParameter = 0;
		I3_LOG(LOG_MASK_PARAMS, "dp reset(%d) reset > defaults to %d", pid, sCurrentParameter);
		return rval;
	}
	sCurrentParameter = idx;
	return 0;
}

// Gets the parameter description for the next parameter.
// Allows the stack to iterate through the parameter list.
// The caller provides a cr_ParameterInfo containing string pointers that will be overwritten.
// The app owns the string pointers which must not be on the stack.
int crcb_parameter_discover_next(cr_ParameterInfo *ppDesc)
{
	if (sCurrentParameter >= NUM_PARAMS)
	{
		I3_LOG(LOG_MASK_PARAMS, "%s: sCurrentParameter (%d) >= NUM_PARAMS (%d)", __FUNCTION__, sCurrentParameter, NUM_PARAMS);
		return cr_ErrorCodes_NO_DATA;
	}
	while (!crcb_access_granted(cr_ServiceIds_PARAMETER_REPO, sParameterDescriptions[sCurrentParameter].id))
	{
		I3_LOG(LOG_MASK_PARAMS, "%s: sCurrentParameter (%d) skip, access not granted", __FUNCTION__, sCurrentParameter);
		sCurrentParameter++;
		if (sCurrentParameter >= NUM_PARAMS)
		{
			I3_LOG(LOG_MASK_PARAMS, "%s: skipped to sCurrentParameter (%d) >= NUM_PARAMS (%d)", __FUNCTION__, sCurrentParameter, NUM_PARAMS);
			return cr_ErrorCodes_NO_DATA;
		}
	}
	*ppDesc = sParameterDescriptions[sCurrentParameter];
	sCurrentParameter++;
	return 0;
}

// Populate a parameter value structure
int crcb_parameter_read(const uint32_t pid, cr_ParameterValue *data)
{
	int rval = 0;
	affirm(data != NULL);
	uint32_t idx;
	rval = sFindIndexFromPid(pid, &idx);
	if (0 != rval)
		return rval;

	/* User code start [Parameter Repository: Parameter Read]
	 * Here is the place to update the data from an external source, and update the return value if necessary */
	/* User code end [Parameter Repository: Parameter Read] */

	*data = sParameterValues[idx];
	return rval;
}

int crcb_parameter_write(const uint32_t pid, const cr_ParameterValue *data)
{
	int rval = 0;
	uint32_t idx;
	rval = sFindIndexFromPid(pid, &idx);
	if (0 != rval)
		return rval;
	I3_LOG(LOG_MASK_PARAMS, "Write param, pid %d (%d)", idx, data->parameter_id);
	I3_LOG(LOG_MASK_PARAMS, "  timestamp %d", data->timestamp);
	I3_LOG(LOG_MASK_PARAMS, "  which %d", data->which_value);

	/* User code start [Parameter Repository: Parameter Write]
	 * Here is the place to apply this change externally, and return an error if necessary */
	/* User code end [Parameter Repository: Parameter Write] */

	sParameterValues[idx].timestamp = data->timestamp;
	sParameterValues[idx].which_value = data->which_value;

	switch ((data->which_value - cr_ParameterValue_uint32_value_tag))
	{
	case cr_ParameterDataType_UINT32:
		sParameterValues[idx].value.uint32_value = data->value.uint32_value;
		break;
	case cr_ParameterDataType_INT32:
		sParameterValues[idx].value.int32_value = data->value.int32_value;
		break;
	case cr_ParameterDataType_FLOAT32:
		sParameterValues[idx].value.float32_value = data->value.float32_value;
		break;
	case cr_ParameterDataType_UINT64:
		sParameterValues[idx].value.uint64_value = data->value.uint64_value;
		break;
	case cr_ParameterDataType_INT64:
		sParameterValues[idx].value.int64_value = data->value.int64_value;
		break;
	case cr_ParameterDataType_FLOAT64:
		sParameterValues[idx].value.float64_value = data->value.float64_value;
		break;
	case cr_ParameterDataType_BOOL:
		sParameterValues[idx].value.bool_value = data->value.bool_value;
		break;
	case cr_ParameterDataType_STRING:
		memcpy(sParameterValues[idx].value.string_value, data->value.string_value, REACH_PVAL_STRING_LEN);
		sParameterValues[idx].value.string_value[REACH_PVAL_STRING_LEN - 1] = 0;
		I3_LOG(LOG_MASK_PARAMS, "String value: %s", sParameterValues[idx].value.string_value);
		break;
	case cr_ParameterDataType_BIT_FIELD:
		sParameterValues[idx].value.bitfield_value = data->value.bitfield_value;
		break;
	case cr_ParameterDataType_ENUMERATION:
		sParameterValues[idx].value.enum_value = data->value.enum_value;
		break;
	case cr_ParameterDataType_BYTE_ARRAY:
		memcpy(sParameterValues[idx].value.bytes_value.bytes, data->value.bytes_value.bytes, REACH_PVAL_BYTES_LEN);
		if (data->value.bytes_value.size > REACH_PVAL_BYTES_LEN)
		{
			LOG_ERROR("Parameter write of bytes has invalid size %d > %d", data->value.bytes_value.size, REACH_PVAL_BYTES_LEN);
			sParameterValues[idx].value.bytes_value.size = REACH_PVAL_BYTES_LEN;
		}
		else
		{
			sParameterValues[idx].value.bytes_value.size = data->value.bytes_value.size;
		}
		LOG_DUMP_MASK(LOG_MASK_PARAMS, "bytes value", sParameterValues[idx].value.bytes_value.bytes, sParameterValues[idx].value.bytes_value.size);
		break;
	default:
		LOG_ERROR("Parameter write which_value %d not recognized.", data->which_value);
		rval = 1;
		break;
	}  // end switch
	return rval;
}

int crcb_parameter_get_count()
{
	int i;
	int numAvailable = 0;
	for (i = 0; i < NUM_PARAMS; i++)
	{
		if (crcb_access_granted(cr_ServiceIds_PARAMETER_REPO, sParameterDescriptions[i].id))
			numAvailable++;
	}
	return numAvailable;
}

// return a number that changes if the parameter descriptions have changed.
uint32_t crcb_compute_parameter_hash(void)
{
	// Note that the layout of the structure sParameterDescriptions differs by compiler.
	// The hash computed on windows won't match that computed on SiLabs.
	uint32_t *ptr = (uint32_t *)sParameterDescriptions;
	// LOG_DUMP_MASK(LOG_MASK_PARAMS, "Raw Params", cptr, sizeof(sParameterDescriptions));

	// The hash should be different based on access permission
	uint32_t hash = 0;
	for (size_t jj = 0; jj < NUM_PARAMS; jj++)
	{
		if (crcb_access_granted(cr_ServiceIds_PARAMETER_REPO, jj))
		{
			ptr = (uint32_t *)&sParameterDescriptions[jj];
			for (size_t i = 0; i < (sizeof(cr_ParameterInfo) / sizeof(uint32_t)); i++)
				hash ^= ptr[i];
		}
	}

#ifdef NUM_EX_PARAMS
	for (int i = 0; i < NUM_EX_PARAMS; i++)
	{
		hash ^= sParameterLabelDescriptions[i].pei_id;
		hash ^= (uint32_t)sParameterLabelDescriptions[i].data_type;
		hash ^= (uint32_t)sParameterLabelDescriptions[i].num_labels;
		for (int j = 0; j < sParameterLabelDescriptions[i].num_labels; j++)
		{
			ptr = (uint32_t *)&sParameterLabelDescriptions[i].labels[j];
			for (size_t k = 0; k < (sizeof(cr_ParamExKey) / sizeof(uint32_t)); k++)
				hash ^= ptr[i];
		}
	}

	I3_LOG(LOG_MASK_PARAMS, "%s: hash 0x%x includes EX.\n", __FUNCTION__, hash);
#else
	I3_LOG(LOG_MASK_PARAMS, "%s: hash 0x%x excludes EX.\n", __FUNCTION__, hash);
#endif // NUM_EX_PARAMS

	return hash;
}
/* Template code end [.c Cygnus Reach Callback Functions] */

/* Template code start [.c Local Functions] */
static int sFindIndexFromPid(uint32_t pid, uint32_t *index)
{
	uint32_t idx;
	for (idx = 0; idx < NUM_PARAMS; idx++)
	{
		if (sParameterDescriptions[idx].id == pid)
		{
			*index = idx;
			return 0;
		}
	}
	return cr_ErrorCodes_INVALID_ID;
}
/* Template code end [.c Local Functions] */
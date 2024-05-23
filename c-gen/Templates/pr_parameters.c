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
static int sCurrentParameter = 0;
static cr_ParameterValue sCr_param_val[NUM_PARAMS];
/* Template code end [.c Local/Extern Variables] */

/* Template code start [.h Global Functions] */
void parameters_init(void)
{
    /* User code start [Parameter Repository: Pre-Init]
     * Here is the place to do any initialization required before individual parameters are initialized */
    /* User code end [Parameter Repository: Pre-Init] */
    memset(sCr_param_val, 0, sizeof(sCr_param_val));
    for (int i = 0; i < NUM_PARAMS; i++)
    {
        sCr_param_val[i].parameter_id = param_desc[i].id;

        // the PID directly maps to the parameter type, just to make it easy.
        switch ((param_desc[i].which_desc - cr_ParameterInfo_uint32_desc_tag))
        {
        case cr_ParameterDataType_UINT32:
            if (param_desc[i].desc.uint32_desc.has_default_value)
                sCr_param_val[i].value.uint32_value = param_desc[i].desc.uint32_desc.default_value;
            break;
        case cr_ParameterDataType_INT32:
            if (param_desc[i].desc.int32_desc.has_default_value)
                sCr_param_val[i].value.int32_value = param_desc[i].desc.int32_desc.default_value;
            break;
        case cr_ParameterDataType_FLOAT32:
            if (param_desc[i].desc.float32_desc.has_default_value)
                sCr_param_val[i].value.float32_value = param_desc[i].desc.float32_desc.default_value;
            break;
        case cr_ParameterDataType_UINT64:
            if (param_desc[i].desc.uint64_desc.has_default_value)
                sCr_param_val[i].value.uint64_value = param_desc[i].desc.uint64_desc.default_value;
            break;
        case cr_ParameterDataType_INT64:
            if (param_desc[i].desc.int64_desc.has_default_value)
                sCr_param_val[i].value.int64_value = param_desc[i].desc.int64_desc.default_value;
            break;
        case cr_ParameterDataType_FLOAT64:
            if (param_desc[i].desc.float64_desc.has_default_value)
                sCr_param_val[i].value.float64_value = param_desc[i].desc.float64_desc.default_value;
            break;
        case cr_ParameterDataType_BOOL:
            if (param_desc[i].desc.bool_desc.has_default_value)
                sCr_param_val[i].value.bool_value = param_desc[i].desc.bool_desc.default_value;
            break;
        case cr_ParameterDataType_STRING:
            if (param_desc[i].desc.string_desc.has_default_value)
            {
                memset(sCr_param_val[i].value.string_value, 0, sizeof(sCr_param_val[i].value.string_value));
                memcpy(sCr_param_val[i].value.string_value, param_desc[i].desc.string_desc.default_value, sizeof(param_desc[i].desc.string_desc.default_value));
            }
            break;
        case cr_ParameterDataType_ENUMERATION:
            if (param_desc[i].desc.enum_desc.has_default_value)
                sCr_param_val[i].value.enum_value = param_desc[i].desc.enum_desc.default_value;
            break;
        case cr_ParameterDataType_BIT_FIELD:
            if (param_desc[i].desc.bitfield_desc.has_default_value)
                sCr_param_val[i].value.bitfield_value = param_desc[i].desc.bitfield_desc.default_value;
            break;
        case cr_ParameterDataType_BYTE_ARRAY:
            if (param_desc[i].desc.bytearray_desc.has_default_value)
            {
                sCr_param_val[i].value.bytes_value.size = param_desc[i].desc.bytearray_desc.default_value.size;
                memcpy(sCr_param_val[i].value.bytes_value.bytes, param_desc[i].desc.bytearray_desc.default_value.bytes, sizeof(param_desc[i].desc.bytearray_desc.default_value.bytes));
            }
            else
            {
                sCr_param_val[i].value.bytes_value.size = param_desc[i].desc.bytearray_desc.max_size;
                memset(sCr_param_val[i].value.bytes_value.bytes, 0, sCr_param_val[i].value.bytes_value.size);
            }
            break;
        default:
            affirm(0);  // should not happen.
            break;
        }  // end switch

        // Convert from description type identifier to value type identifier
        sCr_param_val[i].which_value = (param_desc[i].which_desc - cr_ParameterInfo_uint32_desc_tag) + cr_ParameterValue_uint32_value_tag;

        if (param_desc[i].storage_location == cr_StorageLocation_STORAGE_LOCATION_INVALID || param_desc[i].storage_location > cr_StorageLocation_NONVOLATILE_EXTENDED)
        {
            I3_LOG(LOG_MASK_ERROR, "At param index %d, invalid storage location %d.",
                   i, param_desc[i].storage_location);
        }

        /* User code start [Parameter Repository: Parameter Init]
         * Here is the place to do any initialization specific to a certain parameter */
        /* User code end [Parameter Repository: Parameter Init] */

    } // end for

    /* User code start [Parameter Repository: Post-Init]
     * Here is the place to do any initialization required after parameters have been initialized */
    /* User code end [Parameter Repository: Post-Init] */
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
        I3_LOG(LOG_MASK_PARAMS, "%s: sCurrentParameter (%d) >= NUM_PARAMS (%d)",
               __FUNCTION__, sCurrentParameter, NUM_PARAMS);
        return cr_ErrorCodes_NO_DATA;
    }
    while (!crcb_access_granted(cr_ServiceIds_PARAMETER_REPO, param_desc[sCurrentParameter].id))
    {
        I3_LOG(LOG_MASK_PARAMS, "%s: sCurrentParameter (%d) skip, access not granted",
               __FUNCTION__, sCurrentParameter);
        sCurrentParameter++;
        if (sCurrentParameter >= NUM_PARAMS)
        {
            I3_LOG(LOG_MASK_PARAMS, "%s: skipped to sCurrentParameter (%d) >= NUM_PARAMS (%d)",
                   __FUNCTION__, sCurrentParameter, NUM_PARAMS);
            return cr_ErrorCodes_NO_DATA;
        }
    }
    *ppDesc = param_desc[sCurrentParameter];
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

    *data = sCr_param_val[idx];
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

    sCr_param_val[idx].timestamp = data->timestamp;
    sCr_param_val[idx].which_value = data->which_value;

    switch ((data->which_value - cr_ParameterValue_uint32_value_tag))
    {
    case cr_ParameterDataType_UINT32:
        sCr_param_val[idx].value.uint32_value = data->value.uint32_value;
        break;
    case cr_ParameterDataType_INT32:
        sCr_param_val[idx].value.int32_value = data->value.int32_value;
        break;
    case cr_ParameterDataType_FLOAT32:
        sCr_param_val[idx].value.float32_value = data->value.float32_value;
        break;
    case cr_ParameterDataType_UINT64:
        sCr_param_val[idx].value.uint64_value = data->value.uint64_value;
        break;
    case cr_ParameterDataType_INT64:
        sCr_param_val[idx].value.int64_value = data->value.int64_value;
        break;
    case cr_ParameterDataType_FLOAT64:
        sCr_param_val[idx].value.float64_value = data->value.float64_value;
        break;
    case cr_ParameterDataType_BOOL:
        sCr_param_val[idx].value.bool_value = data->value.bool_value;
        break;
    case cr_ParameterDataType_STRING:
        memcpy(sCr_param_val[idx].value.string_value,
               data->value.string_value, REACH_PVAL_STRING_LEN);
        sCr_param_val[idx].value.string_value[REACH_PVAL_STRING_LEN - 1] = 0;
        I3_LOG(LOG_MASK_PARAMS, "String value: %s",
               sCr_param_val[idx].value.string_value);
        break;
    case cr_ParameterDataType_BIT_FIELD:
        sCr_param_val[idx].value.bitfield_value = data->value.bitfield_value;
        break;
    case cr_ParameterDataType_ENUMERATION:
        sCr_param_val[idx].value.enum_value = data->value.enum_value;
        break;
    case cr_ParameterDataType_BYTE_ARRAY:
        memcpy(sCr_param_val[idx].value.bytes_value.bytes,
               data->value.bytes_value.bytes,
               REACH_PVAL_BYTES_LEN);
        if (data->value.bytes_value.size > REACH_PVAL_BYTES_LEN)
        {
            LOG_ERROR("Parameter write of bytes has invalid size %d > %d",
                      data->value.bytes_value.size, REACH_PVAL_BYTES_LEN);
            sCr_param_val[idx].value.bytes_value.size = REACH_PVAL_BYTES_LEN;
        }
        else
        {
            sCr_param_val[idx].value.bytes_value.size = data->value.bytes_value.size;
        }
        LOG_DUMP_MASK(LOG_MASK_PARAMS, "bytes value",
                      sCr_param_val[idx].value.bytes_value.bytes,
                      sCr_param_val[idx].value.bytes_value.size);
        break;
    default:
        LOG_ERROR("Parameter write which_value %d not recognized.",
                  data->which_value);
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
        if (crcb_access_granted(cr_ServiceIds_PARAMETER_REPO, param_desc[i].id))
            numAvailable++;
    }
    return numAvailable;
}

// return a number that changes if the parameter descriptions have changed.
uint32_t crcb_compute_parameter_hash(void)
{
    // Note that the layout of the structure param_desc differs by compiler.
    // The hash computed on windows won't match that computed on SiLabs.
    uint32_t *ptr = (uint32_t *)param_desc;
    // LOG_DUMP_MASK(LOG_MASK_PARAMS, "Raw Params", cptr, sizeof(param_desc));

    // The hash should be different based on access permission
    uint32_t hash = 0;
    for (size_t jj = 0; jj < NUM_PARAMS; jj++)
    {
        if (crcb_access_granted(cr_ServiceIds_PARAMETER_REPO, jj))
        {
            for (size_t i = 0; i < (sizeof(cr_ParameterInfo) / sizeof(uint32_t)); i++)
                hash ^= ptr[i];
        }
    }

#ifdef NUM_EX_PARAMS
    for (int i = 0; i < NUM_EX_PARAMS; i++)
    {
        hash ^= param_ex_desc[i].pei_id;
        hash ^= (uint32_t)param_ex_desc[i].data_type;
        hash ^= (uint32_t)param_ex_desc[i].num_labels;
        for (int j = 0; j < param_ex_desc[i].num_labels; j++)
        {
            ptr = (uint32_t *)&param_ex_desc[i].labels[j];
            for (size_t k = 0; k < (sizeof(cr_ParamExKey) / sizeof(uint32_t)); k++)
                hash ^= ptr[i];
        }
    }

    I3_LOG(LOG_MASK_PARAMS, "%s: hash 0x%x includes EX.\n",
           __FUNCTION__, hash);
#else
    I3_LOG(LOG_MASK_PARAMS, "%s: hash 0x%x excludes EX.\n",
           __FUNCTION__, hash);
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
        if (param_desc[idx].id == pid)
        {
            *index = idx;
            return 0;
        }
    }
    return cr_ErrorCodes_INVALID_ID;
}
/* Template code end [.c Local Functions] */
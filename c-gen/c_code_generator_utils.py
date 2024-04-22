class ParamRepo:
    main_functions = r'''void init_param_repo()
{
    int rval = 0;
    rval = app_handle_param_repo_pre_init();
    if (rval)
    {
        I3_LOG(LOG_MASK_ERROR, "App-specific param repo pre-init failed (error %d), continuing with init", rval);
    }
    memset(sCr_param_val, 0, sizeof(sCr_param_val));
    for (int i=0; i<NUM_PARAMS; i++)
    {
        sCr_param_val[i].parameter_id = param_desc[i].id;

        // the PID directly maps to the parameter type, just to make it easy.
        switch (param_desc[i].data_type)
        {
        case cr_ParameterDataType_UINT32:
            sCr_param_val[i].which_value = cr_ParameterValue_uint32_value_tag;
            if (param_desc[i].has_default_value)
                sCr_param_val[i].value.uint32_value = (uint32_t)param_desc[i].default_value;
            break;
        case cr_ParameterDataType_INT32:
            sCr_param_val[i].which_value = cr_ParameterValue_sint32_value_tag;
            if (param_desc[i].has_default_value)
                sCr_param_val[i].value.int32_value = (int32_t)param_desc[i].default_value;
            break;
        case cr_ParameterDataType_FLOAT32:
            sCr_param_val[i].which_value = cr_ParameterValue_float32_value_tag;
            if (param_desc[i].has_default_value)
                sCr_param_val[i].value.float32_value = (float)param_desc[i].default_value;
            break;
        case cr_ParameterDataType_UINT64:
            sCr_param_val[i].which_value = cr_ParameterValue_uint64_value_tag;
            if (param_desc[i].has_default_value)
                sCr_param_val[i].value.uint64_value = (uint64_t)param_desc[i].default_value;
            break;
        case cr_ParameterDataType_INT64:
            sCr_param_val[i].which_value = cr_ParameterValue_sint64_value_tag;
            if (param_desc[i].has_default_value)
                sCr_param_val[i].value.int64_value = (int64_t)param_desc[i].default_value;
            break;
        case cr_ParameterDataType_FLOAT64:
            sCr_param_val[i].which_value = cr_ParameterValue_float64_value_tag;
            if (param_desc[i].has_default_value)
                sCr_param_val[i].value.float64_value = param_desc[i].default_value;
            break;
        case cr_ParameterDataType_BOOL:
            sCr_param_val[i].which_value = cr_ParameterValue_bool_value_tag;
            if (param_desc[i].has_default_value)
                sCr_param_val[i].value.bool_value = (bool)param_desc[i].default_value;
            break;
        case cr_ParameterDataType_STRING:
            sCr_param_val[i].which_value = cr_ParameterValue_string_value_tag;
            break;
        case cr_ParameterDataType_ENUMERATION:
            sCr_param_val[i].which_value = cr_ParameterValue_enum_value_tag;
            if (param_desc[i].has_default_value)
                sCr_param_val[i].value.enum_value = (uint32_t)param_desc[i].default_value;
            break;
        case cr_ParameterDataType_BIT_FIELD:
            sCr_param_val[i].which_value = cr_ParameterValue_bitfield_value_tag;
            if (param_desc[i].has_default_value)
                sCr_param_val[i].value.bitfield_value = (uint32_t)param_desc[i].default_value;
            break;
        case cr_ParameterDataType_BYTE_ARRAY:
            sCr_param_val[i].value.bytes_value.size = param_desc[i].size_in_bytes;
            sCr_param_val[i].which_value = cr_ParameterValue_bytes_value_tag;
            break;
        default:
            affirm(0);  // should not happen.
            break;
        }  // end switch

        if (param_desc[i].storage_location == cr_StorageLocation_STORAGE_LOCATION_INVALID || param_desc[i].storage_location > cr_StorageLocation_NONVOLATILE_EXTENDED)
        {
          I3_LOG(LOG_MASK_ERROR, "At param index %d, invalid storage location %d.",
                 i, param_desc[i].storage_location);
        }

        rval = app_handle_param_repo_init(&sCr_param_val[i], &param_desc[i]);
        if (rval != 0)
            I3_LOG(LOG_MASK_ERROR, "At param index %d, failed to initialize data (error %d)", i, rval);

    } // end for
    rval = app_handle_param_repo_post_init();
    if (rval)
    {
        I3_LOG(LOG_MASK_ERROR, "App-specific param repo pre-init failed (error %d), continuing with init", rval);
    }
}

// Populate a parameter value structure
int crcb_parameter_read(const uint32_t pid, cr_ParameterValue *data)
{
    affirm(data != NULL);
    if (pid >= NUM_PARAMS)
        return cr_ErrorCodes_INVALID_PARAMETER;
    int rval = app_handle_param_repo_read(&sCr_param_val[pid]);
    *data = sCr_param_val[pid];
    return rval;
}

int crcb_parameter_write(const uint32_t pid, const cr_ParameterValue *data)
{   
    if (pid >= NUM_PARAMS)
        return cr_ErrorCodes_INVALID_PARAMETER;
    int rval = 0;
    I3_LOG(LOG_MASK_PARAMS, "Write param, pid %d (%d)", pid, data->parameter_id);
    I3_LOG(LOG_MASK_PARAMS, "  timestamp %d", data->timestamp);
    I3_LOG(LOG_MASK_PARAMS, "  which %d", data->which_value);
    rval = app_handle_param_repo_write((cr_ParameterValue *) data);
    if (rval != 0)
    {
        // Invalid data or NVM storage failed
        return rval;
    }
    sCr_param_val[pid].timestamp = data->timestamp;
    sCr_param_val[pid].which_value = data->which_value;

    switch (data->which_value)
    {
        case cr_ParameterValue_uint32_value_tag:
            sCr_param_val[pid].value.uint32_value = data->value.uint32_value;
            break;
        case cr_ParameterValue_sint32_value_tag:
            sCr_param_val[pid].value.int32_value = data->value.int32_value;
            break;
        case cr_ParameterValue_float32_value_tag:
            sCr_param_val[pid].value.float32_value = data->value.float32_value;
            break;
        case cr_ParameterValue_uint64_value_tag:
            sCr_param_val[pid].value.uint64_value = data->value.uint64_value;
            break;
        case cr_ParameterValue_sint64_value_tag:
            sCr_param_val[pid].value.int64_value = data->value.int64_value;
            break;
        case cr_ParameterValue_float64_value_tag:
            sCr_param_val[pid].value.float64_value = data->value.float64_value;
            break;
        case cr_ParameterValue_bool_value_tag:
            sCr_param_val[pid].value.bool_value = data->value.bool_value;
            break;
        case cr_ParameterValue_string_value_tag:
            memcpy(sCr_param_val[pid].value.string_value,
                   data->value.string_value, REACH_PVAL_STRING_LEN);
            sCr_param_val[pid].value.string_value[REACH_PVAL_STRING_LEN-1] = 0;
            I3_LOG(LOG_MASK_PARAMS, "String value: %s",
                   sCr_param_val[pid].value.string_value);
            break;
        case cr_ParameterValue_bitfield_value_tag:
            sCr_param_val[pid].value.bitfield_value = data->value.bitfield_value;
            break;
        case cr_ParameterValue_enum_value_tag:
            sCr_param_val[pid].value.enum_value = data->value.enum_value;
            break;
        case cr_ParameterValue_bytes_value_tag:
            memcpy(sCr_param_val[pid].value.bytes_value.bytes,
                   data->value.bytes_value.bytes, 
                   REACH_PVAL_BYTES_LEN);
            if (data->value.bytes_value.size > REACH_PVAL_BYTES_LEN)
            {
                LOG_ERROR("Parameter write of bytes has invalid size %d > %d",
                          data->value.bytes_value.size, REACH_PVAL_BYTES_LEN);
                sCr_param_val[pid].value.bytes_value.size = REACH_PVAL_BYTES_LEN;
            }
            else
            {
                sCr_param_val[pid].value.bytes_value.size = data->value.bytes_value.size;
            }
            LOG_DUMP_MASK(LOG_MASK_PARAMS, "bytes value",
                          sCr_param_val[pid].value.bytes_value.bytes,
                          sCr_param_val[pid].value.bytes_value.size);
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
    for (i=0; i<NUM_PARAMS; i++)
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
    uint32_t *ptr = (uint32_t*)param_desc;
    size_t sz = sizeof(param_desc)/(sizeof(uint32_t));
    // LOG_DUMP_MASK(LOG_MASK_PARAMS, "Raw Params", cptr, sizeof(param_desc));

    // The hash should be different based on access permission
    uint32_t hash = 0;
    for (size_t jj = 0; jj < NUM_PARAMS; jj++)
    {
        if (crcb_access_granted(cr_ServiceIds_PARAMETER_REPO, jj))
        {
            for (size_t i= 0; i<sizeof(cr_ParameterInfo); i++)
                hash ^= ptr[i];
        }
    }

#ifdef NUM_EX_PARAMS
    ptr = (uint32_t*)param_ex_desc;
    size_t sz1 = sizeof(param_ex_desc)/(sizeof(uint32_t));

    for (size_t i= 0; i<sz1; i++)
        hash ^= ptr[i];

    I3_LOG(LOG_MASK_PARAMS, "%s: hash 0x%x over %d+%d = %d words.\n",
           __FUNCTION__, hash, sz, sz1, sz+sz1);
#else
    I3_LOG(LOG_MASK_PARAMS, "%s: hash 0x%x over %d words.\n",
           __FUNCTION__, hash, sz);
#endif // NUM_EX_PARAMS

    return hash;
}

static int sCurrentParameter = 0;

// Resets the application's pointer into the parameter table such that
// the next call to crcb_parameter_discover_next() will return the
// description of this parameter.
int crcb_parameter_discover_reset(const uint32_t pid)
{
    if (pid >= NUM_PARAMS)
    {
        sCurrentParameter = 0;
        I3_LOG(LOG_MASK_PARAMS, "dp reset(%d) reset defaults to %d", pid, sCurrentParameter);
        return cr_ErrorCodes_INVALID_PARAMETER;
    }
    sCurrentParameter = pid;
    int i;
    sCurrentParameter = 0;  // in case none match
    for (i = 0; i < NUM_PARAMS; i++)
    {
        if (param_desc[i].id == pid) {
            sCurrentParameter = i;
            I3_LOG(LOG_MASK_PARAMS, "dp reset(%d) reset to %d", pid, sCurrentParameter);
            return 0;
        }
    }
    I3_LOG(LOG_MASK_PARAMS, "dp reset(%d) reset defaults to %d", pid, sCurrentParameter);
    return cr_ErrorCodes_INVALID_PARAMETER;
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
}'''

    ext_param_functions = r'''// In parallel to the parameter discovery, use this to find out 
// about enumerations and bitfields
static int sCurrentExParam = 0;
static int sRequestedParamPid = -1; // negative means all

int crcb_parameter_ex_get_count(const int32_t pid)
{
#ifdef NUM_EX_PARAMS
    if (pid < 0)  // all 
        return NUM_EX_PARAMS;

    int num_ex_msgs = 0;

    for (int i=0; i<NUM_EX_PARAMS; i++) {
        if ((int32_t)param_ex_desc[i].associated_pid == pid) {
            num_ex_msgs++;
        }
    }
    return num_ex_msgs;
#else
    return 0;
#endif // NUM_EX_PARAMS
}

int crcb_parameter_ex_discover_reset(const int32_t pid)
{
    // unlike the full params, reset of param_ex always goes to zero.
    sCurrentExParam = 0;
    sRequestedParamPid = pid;
    return 0;
}

int crcb_parameter_ex_discover_next(cr_ParamExInfoResponse *pDesc)
{
    affirm(pDesc);
    pDesc->enumerations_count = 0;
#ifdef NUM_EX_PARAMS
    if (sCurrentExParam>=NUM_EX_PARAMS)
    {
        I3_LOG(LOG_MASK_PARAMS, "%s: No more ex params.", __FUNCTION__);
        return cr_ErrorCodes_INVALID_PARAMETER;
    }

    if (sRequestedParamPid < 0)
    {
        I3_LOG(LOG_MASK_PARAMS, "%s: For all, return param_ex %d.", __FUNCTION__, sCurrentExParam);
        *pDesc = param_ex_desc[sCurrentExParam];
        sCurrentExParam++;
        return 0;
    }

    for (int i=sCurrentExParam; i<NUM_EX_PARAMS; i++)
    {
        if ((int32_t)param_ex_desc[i].associated_pid == sRequestedParamPid)
        {
            I3_LOG(LOG_MASK_PARAMS, "%s: For pid %d, return param_ex %d.",
                   __FUNCTION__, sRequestedParamPid, sCurrentExParam);
            *pDesc = param_ex_desc[i];
            sCurrentExParam = i+1;;
            return 0;
        }
    }
    // should not get here.
    I3_LOG(LOG_MASK_PARAMS, "%s: No more ex params 2.", __FUNCTION__);
#endif // NUM_EX_PARAMS
    return cr_ErrorCodes_INVALID_PARAMETER;
}'''
    weak_access_functions_h = 'int app_handle_param_repo_pre_init(void);\n' \
                              'int app_handle_param_repo_init(cr_ParameterValue *data, const cr_ParameterInfo *desc);\n' \
                              'int app_handle_param_repo_post_init(void);\n' \
                              'int app_handle_param_repo_read(cr_ParameterValue *data);\n' \
                              'int app_handle_param_repo_write(cr_ParameterValue *data);'
    weak_access_functions = r'''int __attribute__((weak)) app_handle_param_repo_pre_init(void)
{
    return 0;
}
int __attribute__((weak)) app_handle_param_repo_init(cr_ParameterValue *data, const cr_ParameterInfo *desc)
{
    (void) desc;
    return app_handle_param_repo_read(data);
}

int __attribute__((weak)) app_handle_param_repo_post_init(void)
{
    return 0;
}

int __attribute__((weak)) app_handle_param_repo_read(cr_ParameterValue *data)
{
    (void) data;
    return 0;
}

int __attribute__((weak)) app_handle_param_repo_write(cr_ParameterValue *data)
{
    (void) data;
    return 0;
}'''


class Files:
    main_functions = r'''int crcb_file_get_description(uint32_t fid, cr_FileInfo *file_desc)
{
    if (fid > NUM_FILES)
        return cr_ErrorCodes_BAD_FILE;
    *file_desc = file_descriptions[fid];
    return 0;
}

int crcb_file_get_file_count()
{
    int i;
    int numAvailable = 0;
    for (i=0; i<NUM_FILES; i++)
    {
        if (crcb_access_granted(cr_ServiceIds_FILES, file_descriptions[i].file_id))
            numAvailable++;
    }
    return numAvailable;
}

static uint8_t sFid_index = 0;
int crcb_file_discover_reset(const uint8_t fid)
{
    if (fid > NUM_FILES)
    {
        I3_LOG(LOG_MASK_ERROR, "crcb_file_discover_reset(%d): invalid FID, using 0.", fid);
        sFid_index = 0;
        return cr_ErrorCodes_BAD_FILE;
    }
    sFid_index = 0;
    for (sFid_index = 0; sFid_index < NUM_FILES; sFid_index++)
    {
        if (file_descriptions[sFid_index].file_id == fid)
        {
            if (!crcb_access_granted(cr_ServiceIds_FILES, file_descriptions[sFid_index].file_id))
            {
                sFid_index = 0;
                break;
            }
            return 0;
        }
    }
    sFid_index = crcb_file_get_file_count();
    I3_LOG(LOG_MASK_PARAMS, "discover file reset (%d) reset defaults to %d", fid, sFid_index);
    return cr_ErrorCodes_INVALID_PARAMETER;
}

int crcb_file_discover_next(cr_FileInfo *file_desc)
{
    if (sFid_index >= NUM_FILES)
    {
        // I3_LOG(LOG_MASK_WARN, "%s: sFid_index (%d) >= NUM_FILES (%d)",
        //        __FUNCTION__, sFid_index, NUM_FILES);
        return cr_ErrorCodes_NO_DATA;
    }

    while (!crcb_access_granted(cr_ServiceIds_FILES, file_desc[sFid_index].file_id))
    {
        I3_LOG(LOG_MASK_FILES, "%s: sFid_index (%d) skip, access not granted",
                   __FUNCTION__, sFid_index);
        sFid_index++;
        if (sCurrentParameter >= NUM_FILES)
        {
            I3_LOG(LOG_MASK_PARAMS, "%s: skipped to sFid_indexsFid_index (%d) >= NUM_FILES (%d)",
                   __FUNCTION__, sFid_index, NUM_FILES);
            return cr_ErrorCodes_NO_DATA;
        }
    }
    *file_desc = file_descriptions[sFid_index++];
    return 0;
}'''


class Commands:
    main_functions = r'''
uint8_t sCommandIndex = 0;

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
        I3_LOG(LOG_MASK_REACH, "%s: Command index %d indicates discovery complete.",
               __FUNCTION__, sCommandIndex);
        return cr_ErrorCodes_NO_DATA;
    }

    while (!crcb_access_granted(cr_ServiceIds_COMMANDS, command_desc[sCommandIndex].id))
    {
        I3_LOG(LOG_MASK_FILES, "%s: sCommandIndex (%d) skip, access not granted",
                   __FUNCTION__, sFid_index);
        sFid_index++;
        if (sCurrentParameter >= NUM_COMMANDS)
        {
            I3_LOG(LOG_MASK_PARAMS, "%s: skipped to sCommandIndex (%d) >= NUM_COMMANDS (%d)",
                   __FUNCTION__, sFid_index, NUM_COMMANDS);
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
        i3_log(LOG_MASK_ERROR, "%s: Command ID %d does not exist.",
               __FUNCTION__, cid);
        return cr_ErrorCodes_INVALID_PARAMETER;
    }

    for (sCommandIndex = 0; sCommandIndex < NUM_COMMANDS; sCommandIndex++)
    {
        if (command_desc[sCommandIndex].id == cid) {
            if (!crcb_access_granted(cr_ServiceIds_COMMANDS, command_desc[sCommandIndex].id))
            {
                sFid_index = 0;
                break;
            }
            I3_LOG(LOG_MASK_PARAMS, "discover command reset (%d) reset to %d", cid, sCurrentParameter);
            return 0;
        }
    }
    sCommandIndex = crcb_get_command_count();
    I3_LOG(LOG_MASK_PARAMS, "discover command reset (%d) reset defaults to %d", cid, sCurrentParameter);
    return cr_ErrorCodes_INVALID_PARAMETER;
}'''


class DeviceInfo:
    main_functions = r'''// The stack will call this function.
// The const copy of the basis in flash is copied to RAM so that the device
// can overwrite varying data like SN and hash.
int crcb_device_get_info(const cr_DeviceInfoRequest *request, cr_DeviceInfoResponse *pDi)
{
    (void) request;
    // The app owns the memory here.
    // The address is returned so that the data can come from flash.
    // memcpy as the structure copy imposes a further address alignment requirement.
    // *pDi = device_info;
    memcpy(pDi, &device_info, sizeof(cr_DeviceInfoResponse));
    I3_LOG(LOG_MASK_REACH, "%s: %s\n", __FUNCTION__, device_info.device_name);

    sprintf(pDi->firmware_version, "%d.%d.%d", APP_MAJOR_VERSION, APP_MINOR_VERSION, APP_PATCH_VERSION);

    snprintf(pDi->device_name, REACH_DEVICE_NAME_LEN, "%s", cr_get_advertised_name());
    return 0;
}'''
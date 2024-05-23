/* Template code start [.h Includes] */
#include <stdint.h>
/* Template code end [.h Includes] */

/* Template code start [.c Includes] */
#include "cr_stack.h"
#include "i3_error.h"
#include "i3_log.h"
/* Template code end [.c Includes] */

/* Template code start [.h Defines] */
/* Template code end [.h Defines] */

/* Template code start [.c Defines] */
#define PARAM_EI_TO_NUM_PEI_RESPONSES(param_ex) ((param_ex.num_labels / 8) + ((param_ex.num_labels % 8) ? 1:0))
/* Template code end [.c Defines] */

/* Template code start [.h Data Types] */
/* Template code end [.h Data Types] */

/* Template code start [.c Data Types] */
typedef struct {
    uint32_t pei_id;
    uint8_t data_type;
    uint8_t num_labels;
    const cr_ParamExKey *labels;
} cr_gen_param_ex_t;
/* Template code end [.c Data Types] */

/* Template code start [.h Global Variables] */
/* Template code end [.h Global Variables] */

/* Template code start [.c Local/Extern Variables] */
static int requested_pei_id = -1;
static int current_pei_index = 0;
static int current_pei_key_index = 0;
/* Template code end [.c Local/Extern Variables] */

/* Template code start [.h Global Functions] */
const char *parameters_get_ei_label(int32_t pei_id, uint32_t enum_bit_position)
{
    uint32_t index = 0;
    if (sFindIndexFromPeiId(pei_id, &index) != 0)
        return 0;
    for (int i = 0; i < param_ex_desc[index].num_labels; i++)
    {
        if (enum_bit_position == param_ex_desc[index].labels[i].id)
            return param_ex_desc[index].labels[i].name;
    }
    return 0;
}
/* Template code end [.h Global Functions] */

/* Template code start [.c Cygnus Reach Callback Functions] */
int crcb_parameter_ex_get_count(const int32_t pid)
{
    if (pid < 0)  // all
	{
		int rval = 0;
        for (int i = 0; i < NUM_EX_PARAMS; i++)
			rval += PARAM_EI_TO_NUM_PEI_RESPONSES(param_ex_desc[i]);
		return rval;
	}

    for (int i=0; i<NUM_EX_PARAMS; i++)
	{
        if (param_ex_desc[i].pei_id == (param_ei_t) pid)
            return PARAM_EI_TO_NUM_PEI_RESPONSES(param_ex_desc[i]);
    }
    return 0;
}

int crcb_parameter_ex_discover_reset(const int32_t pid)
{
	requested_pei_id = pid;
	if (pid < 0)
		current_pei_index = 0;
	else
	{
		current_pei_index = -1;
		for (int i=0; i<NUM_EX_PARAMS; i++)
		{
			if (param_ex_desc[i].pei_id == (param_ei_t) pid)
			{
				current_pei_index = i;
				break;
			}
		}
	}
	current_pei_key_index = 0;
	return 0;
}

int crcb_parameter_ex_discover_next(cr_ParamExInfoResponse *pDesc)
{
    affirm(pDesc);

	if (current_pei_index < 0)
	{
		I3_LOG(LOG_MASK_PARAMS, "%s: No more ex params.", __FUNCTION__);
        return cr_ErrorCodes_INVALID_ID;
	}
	else
	{
		pDesc->pei_id = param_ex_desc[current_pei_index].pei_id;
		pDesc->data_type = param_ex_desc[current_pei_index].data_type;
		pDesc->keys_count = param_ex_desc[current_pei_index].num_labels - current_pei_key_index;
		if (pDesc->keys_count > 8)
			pDesc->keys_count = 8;
		memcpy(&pDesc->keys, &param_ex_desc[current_pei_index].labels[current_pei_key_index], pDesc->keys_count * sizeof(cr_ParamExKey));
		current_pei_key_index += pDesc->keys_count;
		if (current_pei_key_index >= param_ex_desc[current_pei_index].num_labels)
		{
			if (requested_pei_id == -1)
			{
				// Advance to the next pei_id index
				current_pei_index++;
				if (current_pei_index >= NUM_EX_PARAMS)
					current_pei_index = -1;
			}
			else
			{
				// Out of data for the selected pei_id
				current_pei_index = -1;
			}
			current_pei_key_index = 0;
		}
	}
	return 0;
}
/* Template code end [.c Cygnus Reach Callback Functions] */

/* Template code start [.c Local Functions] */
static int sFindIndexFromPeiId(uint32_t pei_id, uint32_t *index)
{
    uint32_t idx;
    for (idx=0; idx<NUM_EX_PARAMS; idx++) {
        if (param_ex_desc[idx].pei_id == pei_id) {
            *index = idx;
            return 0;
        }
    }
    return cr_ErrorCodes_INVALID_ID;
}
/* Template code end [.c Local Functions] */
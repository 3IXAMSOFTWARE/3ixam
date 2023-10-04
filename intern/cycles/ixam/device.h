

#ifndef __IXAM_DEVICE_H__
#define __IXAM_DEVICE_H__

#include "MEM_guardedalloc.h"
#include "RNA_access.h"
#include "RNA_ixam_cpp.h"
#include "RNA_types.h"

#include "device/device.h"

CCL_NAMESPACE_BEGIN

/* Get number of threads to use for rendering. */
int ixam_device_threads(BL::Scene &b_scene);

/* Convert 3IXAM settings to device specification. */
DeviceInfo ixam_device_info(BL::Preferences &b_preferences,
                               BL::Scene &b_scene,
                               bool background);

CCL_NAMESPACE_END

#endif /* __IXAM_DEVICE_H__ */
